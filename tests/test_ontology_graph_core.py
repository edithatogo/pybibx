"""Regression tests for ontology facets and RustWorkX graph builders."""

from __future__ import annotations

import networkx as nx
import pytest
from pydantic import ValidationError

from pybibx.graph import GraphBuildError, build_citation_graph, build_coauthorship_graph, to_networkx
from pybibx.schemas import (
    Author,
    Citation,
    CitationIntent,
    CitoCitationFacet,
    CslItem,
    FabioWorkFacet,
    FrapoFundingFacet,
    OntologyNamespace,
    OntologyTerm,
    OrcidIdentityFacet,
    OrgUnitFacet,
    PsoStatusFacet,
    RorOrganizationFacet,
    SemanticOntologyBundle,
    Work,
    WorkType,
)

EXPECTED_EDGE_COUNT = 1
EXPECTED_NODE_COUNT = 2
REFUTES_EDGE_WEIGHT = 2.0
TWO_SHARED_PUBLICATIONS_WEIGHT = 2.0


def test_additive_ontology_bundle_preserves_required_namespaces() -> None:
    bundle = SemanticOntologyBundle(
        schema_org_type="ScholarlyArticle",
        cito=(
            CitoCitationFacet(
                source_work_id="W1",
                target_work_id="W2",
                intent=CitationIntent.REFUTES,
                context_text="This finding contradicts prior work.",
                evidence_ids=("e1",),
                confidence=0.9,
            ),
        ),
        fabio=FabioWorkFacet(work_type=WorkType.JOURNAL_ARTICLE),
        frapo=(FrapoFundingFacet(funder_id="grant:f1", funder_name="Example Funder", grant_number="G-1"),),
        pso=PsoStatusFacet(),
        org=(OrgUnitFacet(name="Example Lab", ror_id="https://ror.org/03yrm5c26"),),
        ror=(RorOrganizationFacet(ror_id="https://ror.org/03yrm5c26", name="Example University", country_code="nz"),),
        orcid=(
            OrcidIdentityFacet(
                orcid="0000-0002-1825-0097",
                display_name="Ada Lovelace",
                affiliation_ror_ids=("https://ror.org/03yrm5c26",),
            ),
        ),
        csl=CslItem(id="W1", type="article-journal", title="Ontology paper", DOI="10.1234/ONTOLOGY"),
    )

    assert bundle.cito[0].term.prefixed_id == "cito:refutes"
    assert bundle.fabio.work_type is WorkType.JOURNAL_ARTICLE
    assert bundle.org[0].ror_id == "https://ror.org/03yrm5c26"
    assert bundle.ror[0].country_code == "NZ"
    assert bundle.orcid[0].orcid == "https://orcid.org/0000-0002-1825-0097"
    assert bundle.csl is not None
    assert bundle.csl.doi == "10.1234/ontology"


def test_ontology_terms_derive_prefixed_ids_and_iris() -> None:
    term = OntologyTerm(namespace=OntologyNamespace.FABIO, term="JournalArticle", label="Journal article")

    assert term.prefixed_id == "fabio:JournalArticle"
    assert term.iri == "http://purl.org/spar/fabio/JournalArticle"


def test_ontology_identifier_validation_fails_closed() -> None:
    with pytest.raises(ValidationError, match="ROR ID"):
        OrgUnitFacet(name="Bad institution", ror_id="https://example.test/not-ror")

    with pytest.raises(ValidationError, match="ORCID"):
        OrcidIdentityFacet(orcid="bad-orcid", display_name="Bad Author")


def test_rustworkx_citation_graph_exports_to_networkx() -> None:
    source = Work(
        work_id="W1",
        title="Source",
        doi="10.1234/SOURCE",
        authors=(Author(display_name="Ada Lovelace", orcid="0000-0002-1825-0097"),),
    )
    target = Work(work_id="W2", title="Target", doi="10.1234/TARGET")
    citation = Citation(
        source_work_id=source.work_id,
        target_work_id=target.work_id,
        intent=CitationIntent.REFUTES,
        context_text="The newer result refutes the older one.",
        evidence_ids=("e1",),
    )

    result = build_citation_graph((source, target), (citation,))
    exported = to_networkx(result)

    assert result.graph.num_nodes() == EXPECTED_NODE_COUNT
    assert result.graph.num_edges() == EXPECTED_EDGE_COUNT
    assert isinstance(exported, nx.DiGraph)
    assert exported.nodes["W1"]["doi"] == "10.1234/source"
    assert exported["W1"]["W2"]["intent"] == CitationIntent.REFUTES.value
    assert exported["W1"]["W2"]["weight"] == REFUTES_EDGE_WEIGHT
    assert exported["W1"]["W2"]["context_text"] == "The newer result refutes the older one."


def test_citation_graph_rejects_unknown_work_references() -> None:
    with pytest.raises(GraphBuildError, match="unknown works"):
        build_citation_graph(
            (Work(work_id="W1", title="Source"),),
            (Citation(source_work_id="W1", target_work_id="missing"),),
        )


def test_coauthorship_graph_aggregates_shared_publications_and_exports_networkx() -> None:
    ada = Author(display_name="Ada Lovelace", orcid="0000-0002-1825-0097")
    grace = Author(display_name="Grace Hopper", orcid="0000-0002-1694-233X")
    works = (
        Work(work_id="W1", title="Joint paper 1", authors=(ada, grace)),
        Work(work_id="W2", title="Joint paper 2", authors=(grace, ada)),
    )

    result = build_coauthorship_graph(works)
    exported = to_networkx(result)

    assert result.graph.num_nodes() == EXPECTED_NODE_COUNT
    assert result.graph.num_edges() == EXPECTED_EDGE_COUNT
    assert not exported.is_directed()
    assert exported[ada.orcid][grace.orcid]["kind"] == "coauthorship"
    assert exported[ada.orcid][grace.orcid]["weight"] == TWO_SHARED_PUBLICATIONS_WEIGHT
