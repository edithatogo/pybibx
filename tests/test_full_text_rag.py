"""Regression tests for legal full-text routing and evidence-grounded RAG primitives."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from pybibx.rag import (
    EmbeddingRecord,
    FullTextSourceKind,
    GroundedExtraction,
    ParserBackend,
    VectorStoreRecord,
    build_evidence_set,
    chunk_markdown,
    create_embedding_records,
    evaluate_pdf_parsers,
    plan_local_rag_pipeline,
    route_preprint_full_text,
    route_unpaywall_full_text,
)
from pybibx.schemas import ProviderName

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "tests" / "fixtures" / "providers"
EXPECTED_PARSER_COUNT = 2
VECTOR_DIMENSIONS = 3


def _fixture(name: str) -> dict[str, object]:
    payload = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_unpaywall_routes_only_open_access_full_text() -> None:
    route = route_unpaywall_full_text(_fixture("unpaywall.json"), work_id="W1")

    assert route is not None
    assert route.work_id == "W1"
    assert route.source_kind is FullTextSourceKind.UNPAYWALL
    assert route.provider is ProviderName.UNPAYWALL
    assert route.url == "https://example.test/paper.pdf"
    assert route.doi == "10.1234/unpaywall.fixture"
    assert route.is_legal is True

    assert route_unpaywall_full_text({"doi": "10.1234/closed", "is_oa": False}) is None


@pytest.mark.parametrize(
    ("provider", "fixture_name", "expected_kind"),
    [
        (ProviderName.ARXIV, "arxiv.json", FullTextSourceKind.ARXIV),
        (ProviderName.BIORXIV, "biorxiv.json", FullTextSourceKind.BIORXIV),
        (ProviderName.MEDRXIV, "medrxiv.json", FullTextSourceKind.MEDRXIV),
    ],
)
def test_preprint_routes_legal_pdf_locations(
    provider: ProviderName,
    fixture_name: str,
    expected_kind: FullTextSourceKind,
) -> None:
    route = route_preprint_full_text(provider, _fixture(fixture_name))

    assert route.provider is provider
    assert route.source_kind is expected_kind
    assert route.is_legal is True
    assert route.url.endswith(".pdf")


def test_docling_and_pdfmux_are_evaluated_behind_common_parser_interface() -> None:
    evaluations = evaluate_pdf_parsers()

    assert len(evaluations) == EXPECTED_PARSER_COUNT
    assert {item.backend for item in evaluations} == {ParserBackend.DOCLING, ParserBackend.PDFMUX}
    docling = next(item for item in evaluations if item.backend is ParserBackend.DOCLING)
    pdfmux = next(item for item in evaluations if item.backend is ParserBackend.PDFMUX)
    assert docling.local_execution is True
    assert pdfmux.terms_review_required is True
    assert pdfmux.requires_credentials is True


def test_markdown_chunking_preserves_section_locators_for_evidence() -> None:
    chunks = chunk_markdown(
        work_id="W1",
        source_locator="https://example.test/paper.pdf",
        markdown="# Methods\nSentence one. Sentence two.\n# Results\nResult sentence.",
        max_chars=200,
    )

    assert [chunk.section_path for chunk in chunks] == [("Methods",), ("Results",)]
    assert chunks[0].source_locator == "https://example.test/paper.pdf#chunk=1"
    assert chunks[0].start_char < chunks[0].end_char


def test_embedding_and_lancedb_records_remain_chunk_aligned() -> None:
    chunks = chunk_markdown(
        work_id="W1",
        source_locator="https://example.test/paper.pdf",
        markdown="# Results\nEvidence sentence.",
    )
    embeddings = create_embedding_records(chunks, ((0.1, 0.2, 0.3),), model_name="BAAI/bge-small-en-v1.5")
    record = VectorStoreRecord(chunk=chunks[0], embedding=embeddings[0])

    assert isinstance(embeddings[0], EmbeddingRecord)
    assert len(embeddings[0].vector) == VECTOR_DIMENSIONS
    assert record.chunk.chunk_id == record.embedding.chunk_id

    with pytest.raises(ValueError, match="same length"):
        create_embedding_records(chunks, (), model_name="BAAI/bge-small-en-v1.5")

    with pytest.raises(ValidationError, match="chunk_id"):
        VectorStoreRecord(chunk=chunks[0], embedding=EmbeddingRecord(chunk_id="other", model_name="m", vector=(1.0,)))


def test_evidence_grounded_extraction_requires_present_supporting_chunks() -> None:
    chunks = chunk_markdown(
        work_id="W1",
        source_locator="https://example.test/paper.pdf",
        markdown="# Results\nThis result supports the extracted claim.",
    )
    claim = "The paper reports a supporting result."
    evidence_set = build_evidence_set(
        evidence_set_id="evidence:1",
        claim_text=claim,
        chunks=chunks,
        supporting_chunk_ids=(chunks[0].chunk_id,),
    )
    extraction = GroundedExtraction(
        extraction_id="extract:1",
        work_id="W1",
        claim_text=claim,
        evidence_set=evidence_set,
        extraction_backend="instructor:pydantic",
    )

    assert extraction.evidence_set.supporting_item_ids == (chunks[0].chunk_id,)
    assert extraction.evidence_set.items[0].quote == chunks[0].text

    with pytest.raises(ValueError, match="supporting chunks"):
        build_evidence_set(
            evidence_set_id="evidence:bad",
            claim_text=claim,
            chunks=chunks,
            supporting_chunk_ids=("missing",),
        )


def test_pipeline_plan_keeps_only_legal_credential_free_routes() -> None:
    open_route = route_unpaywall_full_text(_fixture("unpaywall.json"))
    assert open_route is not None
    plan = plan_local_rag_pipeline((open_route, open_route.model_copy(update={"requires_credentials": True})))

    assert plan.evidence_required is True
    assert plan.routes == (open_route,)
    assert plan.embedding_backend.value == "fastembed"
    assert plan.vector_backend.value == "lancedb"
