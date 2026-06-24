"""Regression tests for legal full-text routing and evidence-grounded RAG primitives."""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import cast

import pytest
from pydantic import ValidationError

from pybibx.rag import (
    EmbeddingRecord,
    FullTextSourceKind,
    GroundedExtraction,
    ParsedDocument,
    ParserBackend,
    PdfParseCandidate,
    VectorStoreRecord,
    build_evidence_set,
    chunk_markdown,
    create_embedding_records,
    evaluate_pdf_parsers,
    plan_local_rag_pipeline,
    route_preprint_full_text,
    route_unpaywall_full_text,
)
from pybibx.schemas import EvidenceItem, EvidenceSet, ProviderName

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "tests" / "fixtures" / "providers"
EXPECTED_PARSER_COUNT = 2
VECTOR_DIMENSIONS = 3
LONG_CHUNK_LENGTH = 450
CHUNK_MAX_CHARS = 200
EXPECTED_LONG_CHUNKS = 3


def _fixture(name: str) -> dict[str, object]:
    payload = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return cast("dict[str, object]", payload)


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
    assert (
        route_unpaywall_full_text(
            {
                "doi": "10.1234/ftp",
                "is_oa": True,
                "best_oa_location": {"url_for_pdf": "ftp://example.test/paper.pdf"},
            },
        )
        is None
    )
    assert (
        route_unpaywall_full_text(
            {
                "doi": "10.1234/landing",
                "is_oa": True,
                "best_oa_location": {"url": "https://example.test/article"},
            },
        )
        is None
    )


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


def test_preprint_routes_reject_spoofed_or_mismatched_sources() -> None:
    with pytest.raises(ValueError, match="arXiv"):
        route_preprint_full_text(ProviderName.ARXIV, {"id": "https://example.test/paywalled"})

    arxiv_route = route_preprint_full_text(ProviderName.ARXIV, {"id": "https://arxiv.org/abs/2601.00001v1"})
    assert arxiv_route.work_id == "arxiv:2601.00001v1"

    medrxiv_payload = _fixture("medrxiv.json")
    with pytest.raises(ValueError, match="payload server"):
        route_preprint_full_text(ProviderName.BIORXIV, medrxiv_payload)


def test_docling_and_pdfmux_are_evaluated_behind_common_parser_interface() -> None:
    evaluations = evaluate_pdf_parsers()

    assert len(evaluations) == EXPECTED_PARSER_COUNT
    assert {item.backend for item in evaluations} == {ParserBackend.DOCLING, ParserBackend.PDFMUX}
    docling = next(item for item in evaluations if item.backend is ParserBackend.DOCLING)
    pdfmux = next(item for item in evaluations if item.backend is ParserBackend.PDFMUX)
    assert docling.local_execution is True
    assert pdfmux.terms_review_required is True
    assert pdfmux.requires_credentials is True

    route = route_unpaywall_full_text(_fixture("unpaywall.json"))
    assert route is not None
    candidate = PdfParseCandidate(route=route, parser_backend=ParserBackend.DOCLING)
    parsed = ParsedDocument(
        candidate=candidate,
        markdown="# Results\nParsed text.",
        source_locator=route.url,
        page_count=1,
    )
    assert parsed.candidate.parser_backend is ParserBackend.DOCLING

    with pytest.raises(ValidationError, match="credential-free"):
        PdfParseCandidate(
            route=route.model_copy(update={"requires_credentials": True}),
            parser_backend=ParserBackend.PDFMUX,
        )


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


def test_markdown_chunking_splits_long_sentence_like_sections() -> None:
    chunks = chunk_markdown(
        work_id="W1",
        source_locator="https://example.test/paper.pdf",
        markdown=f"# Results\n{'x' * LONG_CHUNK_LENGTH}",
        max_chars=CHUNK_MAX_CHARS,
    )

    assert len(chunks) > 1
    assert all(len(chunk.text) <= CHUNK_MAX_CHARS for chunk in chunks)
    assert [chunk.source_locator for chunk in chunks] == [
        "https://example.test/paper.pdf#chunk=1",
        "https://example.test/paper.pdf#chunk=2",
        "https://example.test/paper.pdf#chunk=3",
    ]
    assert len(chunks) == EXPECTED_LONG_CHUNKS


def test_markdown_chunk_ids_include_source_fingerprint_and_nested_sections() -> None:
    left = chunk_markdown(
        work_id="W1",
        source_locator="https://example.test/left.pdf",
        markdown="# Results\n## Table 1\nNested result.",
    )
    right = chunk_markdown(
        work_id="W1",
        source_locator="https://example.test/right.pdf",
        markdown="# Results\n## Table 1\nNested result.",
    )

    assert left[0].section_path == ("Results", "Table 1")
    assert right[0].section_path == ("Results", "Table 1")
    assert left[0].chunk_id != right[0].chunk_id


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
    lancedb_record = record.to_lancedb_record()
    assert lancedb_record["id"] == chunks[0].chunk_id
    assert lancedb_record["vector"] == [0.1, 0.2, 0.3]
    assert lancedb_record["embedding_model"] == "BAAI/bge-small-en-v1.5"

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

    with pytest.raises(ValueError, match="unique"):
        build_evidence_set(
            evidence_set_id="evidence:duplicate",
            claim_text=claim,
            chunks=chunks,
            supporting_chunk_ids=(chunks[0].chunk_id, chunks[0].chunk_id),
        )


def test_grounded_extraction_rejects_quote_less_or_cross_work_evidence() -> None:
    evidence = EvidenceSet(
        evidence_set_id="manual",
        claim_text="Claim",
        items=(
            EvidenceItem(
                evidence_id="W1:source:abcdef123456:chunk:1",
                source_provider=ProviderName.UNPAYWALL,
                source_locator="https://example.test/paper.pdf#chunk=1",
            ),
        ),
        supporting_item_ids=("W1:source:abcdef123456:chunk:1",),
    )

    with pytest.raises(ValidationError, match="concrete chunk quotes"):
        GroundedExtraction(
            extraction_id="extract:quote-less",
            work_id="W1",
            claim_text="Claim",
            evidence_set=evidence,
            extraction_backend="instructor:pydantic",
        )

    chunks = chunk_markdown(
        work_id="W1",
        source_locator="https://example.test/paper.pdf",
        markdown="# Results\nEvidence.",
    )
    cross_work_evidence = build_evidence_set(
        evidence_set_id="cross-work",
        claim_text="Claim",
        chunks=chunks,
        supporting_chunk_ids=(chunks[0].chunk_id,),
    )
    with pytest.raises(ValidationError, match="work_id"):
        GroundedExtraction(
            extraction_id="extract:cross-work",
            work_id="W2",
            claim_text="Claim",
            evidence_set=cross_work_evidence,
            extraction_backend="instructor:pydantic",
        )

    with pytest.raises(ValidationError, match="less than or equal to 1"):
        GroundedExtraction(
            extraction_id="extract:bad-confidence",
            work_id="W1",
            claim_text="Claim",
            evidence_set=cross_work_evidence,
            extraction_backend="instructor:pydantic",
            confidence=1.5,
        )


def test_pipeline_plan_keeps_only_legal_credential_free_routes() -> None:
    open_route = route_unpaywall_full_text(_fixture("unpaywall.json"))
    assert open_route is not None
    plan = plan_local_rag_pipeline((open_route, open_route.model_copy(update={"requires_credentials": True})))

    assert plan.evidence_required is True
    assert plan.routes == (open_route,)
    assert plan.embedding_backend.value == "fastembed"
    assert plan.vector_backend.value == "lancedb"


def test_pipeline_plan_rejects_empty_evidence_routes() -> None:
    open_route = route_unpaywall_full_text(_fixture("unpaywall.json"))
    assert open_route is not None

    with pytest.raises(ValidationError, match="at least one legal credential-free route"):
        plan_local_rag_pipeline(())

    with pytest.raises(ValidationError, match="at least one legal credential-free route"):
        plan_local_rag_pipeline((open_route.model_copy(update={"requires_credentials": True}),))


def test_rag_import_does_not_load_optional_or_legacy_runtime_dependencies() -> None:
    code = textwrap.dedent(
        """
        import sys
        from importlib.abc import MetaPathFinder

        blocked = {
            'docling', 'pdfmux', 'fastembed', 'lancedb', 'llama_index', 'instructor', 'dspy',
            'pydantic_ai', 'pandas', 'numpy', 'scipy', 'sklearn', 'torch', 'transformers', 'gensim',
            'flask', 'pybibx.base', 'pybibx.base.pbx',
        }

        class Blocker(MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                if any(fullname == item or fullname.startswith(f'{item}.') for item in blocked):
                    raise AssertionError(fullname)
                return None

        sys.meta_path.insert(0, Blocker())
        from pybibx.rag import route_unpaywall_full_text

        assert route_unpaywall_full_text is not None
        loaded = blocked.intersection(sys.modules)
        assert not loaded, sorted(loaded)
        """,
    )

    subprocess.run([sys.executable, "-c", code], check=True)  # noqa: S603
