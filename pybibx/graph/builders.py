from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from itertools import combinations
from typing import cast

import networkx as nx
import rustworkx as rx
from pydantic import Field

from pybibx.schemas import Author, Citation, CitationIntent, Work
from pybibx.schemas.records import StrictSchemaModel


class GraphBuildError(ValueError):
    pass


class GraphNodeKind(StrEnum):
    WORK = "work"
    AUTHOR = "author"


class SemanticEdgeKind(StrEnum):
    CITATION = "citation"
    COAUTHORSHIP = "coauthorship"


class GraphNodePayload(StrictSchemaModel):
    node_id: str = Field(min_length=1)
    kind: GraphNodeKind
    label: str = Field(min_length=1)
    doi: str | None = None
    orcid: str | None = None


class GraphEdgePayload(StrictSchemaModel):
    source_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    kind: SemanticEdgeKind
    weight: float = Field(default=1.0, ge=0.0)
    intent: CitationIntent | None = None
    context_text: str | None = None
    evidence_ids: tuple[str, ...] = Field(default_factory=tuple)


type RustworkxGraph = rx.PyDiGraph[GraphNodePayload, GraphEdgePayload] | rx.PyGraph[GraphNodePayload, GraphEdgePayload]
type NetworkxGraph = (
    nx.DiGraph[str, dict[str, object], dict[str, object]] | nx.Graph[str, dict[str, object], dict[str, object]]
)


@dataclass(frozen=True)
class GraphBuildResult:
    graph: RustworkxGraph
    node_indices: dict[str, int]


def build_citation_graph(
    works: list[Work] | tuple[Work, ...],
    citations: list[Citation] | tuple[Citation, ...],
) -> GraphBuildResult:
    graph = rx.PyDiGraph()
    node_indices = _add_work_nodes(graph, works)
    missing = sorted(
        {
            work_id
            for citation in citations
            for work_id in (citation.source_work_id, citation.target_work_id)
            if work_id not in node_indices
        },
    )
    if missing:
        msg = f"citations reference unknown works: {missing}"
        raise GraphBuildError(msg)

    for citation in citations:
        graph.add_edge(
            node_indices[citation.source_work_id],
            node_indices[citation.target_work_id],
            GraphEdgePayload(
                source_id=citation.source_work_id,
                target_id=citation.target_work_id,
                kind=SemanticEdgeKind.CITATION,
                weight=_citation_weight(citation.intent),
                intent=citation.intent,
                context_text=citation.context_text,
                evidence_ids=citation.evidence_ids,
            ),
        )
    return GraphBuildResult(graph=graph, node_indices=node_indices)


def build_coauthorship_graph(works: list[Work] | tuple[Work, ...]) -> GraphBuildResult:
    graph = rx.PyGraph()
    node_indices: dict[str, int] = {}
    edge_weights: dict[tuple[str, str], float] = {}

    for work in works:
        author_ids = [_author_id(author) for author in work.authors]
        for author in work.authors:
            author_id = _author_id(author)
            if author_id not in node_indices:
                node_indices[author_id] = graph.add_node(
                    GraphNodePayload(
                        node_id=author_id,
                        kind=GraphNodeKind.AUTHOR,
                        label=author.display_name,
                        orcid=author.orcid,
                    ),
                )
        for left_id, right_id in combinations(sorted(set(author_ids)), 2):
            key = (left_id, right_id)
            edge_weights[key] = edge_weights.get(key, 0.0) + 1.0

    for (left_id, right_id), weight in edge_weights.items():
        graph.add_edge(
            node_indices[left_id],
            node_indices[right_id],
            GraphEdgePayload(
                source_id=left_id,
                target_id=right_id,
                kind=SemanticEdgeKind.COAUTHORSHIP,
                weight=weight,
            ),
        )

    return GraphBuildResult(graph=graph, node_indices=node_indices)


def to_networkx(result: GraphBuildResult) -> NetworkxGraph:
    network = cast(
        "NetworkxGraph",
        nx.DiGraph() if isinstance(result.graph, rx.PyDiGraph) else nx.Graph(),
    )
    for node_index in result.graph.node_indices():
        payload = result.graph.get_node_data(node_index)
        network.add_node(payload.node_id, **payload.model_dump(mode="json"))
    for source_index, target_index, payload in result.graph.weighted_edge_list():
        source = result.graph.get_node_data(source_index)
        target = result.graph.get_node_data(target_index)
        network.add_edge(source.node_id, target.node_id, **payload.model_dump(mode="json"))
    return network


def _add_work_nodes(graph: RustworkxGraph, works: list[Work] | tuple[Work, ...]) -> dict[str, int]:
    node_indices: dict[str, int] = {}
    for work in works:
        if work.work_id in node_indices:
            msg = f"duplicate work_id in graph input: {work.work_id}"
            raise GraphBuildError(msg)
        node_indices[work.work_id] = graph.add_node(
            GraphNodePayload(
                node_id=work.work_id,
                kind=GraphNodeKind.WORK,
                label=work.title,
                doi=work.doi,
            ),
        )
    return node_indices


def _author_id(author: Author) -> str:
    return author.orcid or f"name:{author.display_name.casefold()}"


def _citation_weight(intent: CitationIntent) -> float:
    return {
        CitationIntent.REFUTES: 2.0,
        CitationIntent.SUPPORTS: 1.5,
        CitationIntent.USES_METHOD_FROM: 1.4,
        CitationIntent.EXTENDS: 1.3,
        CitationIntent.DISCUSSES: 1.1,
        CitationIntent.PROVIDES_BACKGROUND: 0.8,
        CitationIntent.CITES: 1.0,
    }[intent]
