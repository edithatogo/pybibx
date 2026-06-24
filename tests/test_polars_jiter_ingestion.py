"""Regression tests for Polars/Jiter ingestion helpers."""

from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

import pybibx.ingestion.parsers as ingestion_parsers
from pybibx.ingestion import IngestionError, ingest_provider_file, load_json_payload, scan_jsonl, scan_tabular
from pybibx.providers import DEFAULT_PROVIDER_REGISTRY
from pybibx.schemas import InputFormat, ProviderName, WorkType
from pybibx.versioning import VersionedSurface

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "tests" / "fixtures" / "providers"


def assert_compatibility_metadata(
    result_input: InputFormat,
    result_provider: ProviderName,
    result_work_index: int = 0,
) -> None:
    result = ingest_provider_file(
        FIXTURES
        / {
            InputFormat.JSON: "openalex.json",
            InputFormat.CSV: "scopus_export.csv",
            InputFormat.TSV: "web_of_science_export.txt",
            InputFormat.BIBTEX: "google_scholar_export.bib",
        }[result_input],
        provider=result_provider,
    )
    work = result.works[result_work_index]

    assert work.compatibility.provider is not None
    assert work.compatibility.provider.name == result_provider.value
    assert work.compatibility.input is not None
    assert work.compatibility.input.name == result_input.value
    assert work.compatibility.library.surface is VersionedSurface.LIBRARY
    assert work.compatibility.schema_profile.surface is VersionedSurface.SCHEMA
    assert work.compatibility.settings.surface is VersionedSurface.SETTINGS


@pytest.mark.parametrize(
    ("provider", "fixture_name"),
    [
        (ProviderName.OPENALEX, "openalex.json"),
        (ProviderName.CROSSREF, "crossref.json"),
        (ProviderName.PUBMED, "pubmed.json"),
        (ProviderName.MEDLINE, "medline.json"),
        (ProviderName.OPENCITATIONS, "opencitations.json"),
        (ProviderName.SEMANTIC_SCHOLAR, "semantic_scholar.json"),
        (ProviderName.ROR, "ror.json"),
        (ProviderName.ORCID, "orcid.json"),
        (ProviderName.UNPAYWALL, "unpaywall.json"),
        (ProviderName.ARXIV, "arxiv.json"),
        (ProviderName.BIORXIV, "biorxiv.json"),
        (ProviderName.MEDRXIV, "medrxiv.json"),
    ],
)
def test_json_fixtures_ingest_with_jiter(provider: ProviderName, fixture_name: str) -> None:
    result = ingest_provider_file(FIXTURES / fixture_name, provider=provider)

    assert result.provider is provider
    assert result.input_format is InputFormat.JSON
    assert len(result.works) == 1
    assert result.works[0].source_provider is provider
    assert result.works[0].compatibility.provider is not None
    assert result.works[0].compatibility.provider.surface is VersionedSurface.PROVIDER


def test_jiter_loader_returns_raw_payload_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[bytes] = []
    original_from_json = ingestion_parsers.jiter.from_json

    def spy_from_json(data: bytes) -> object:
        calls.append(data)
        return original_from_json(data)

    monkeypatch.setattr(ingestion_parsers.jiter, "from_json", spy_from_json)

    payload = load_json_payload(FIXTURES / "openalex.json")

    assert isinstance(payload, dict)
    assert payload["id"] == "https://openalex.org/W123"
    assert calls


def test_openalex_jsonl_ingests_with_polars_lazy_scan(tmp_path: Path) -> None:
    path = tmp_path / "openalex.jsonl"
    path.write_text(
        '{"id":"https://openalex.org/W1","title":"First JSONL Work","doi":"https://doi.org/10.1234/jsonl.1","publication_year":2025}\n'
        '{"id":"https://openalex.org/W2","title":"Second JSONL Work","doi":"https://doi.org/10.1234/jsonl.2","publication_year":2026}',
        encoding="utf-8",
    )

    frame = scan_jsonl(path)
    result = ingest_provider_file(path, provider=ProviderName.OPENALEX)

    assert isinstance(frame, pl.LazyFrame)
    assert result.input_format is InputFormat.JSONL
    assert result.compatibility.input is not None
    assert result.compatibility.input.name == "jsonl"
    assert [work.title for work in result.works] == ["First JSONL Work", "Second JSONL Work"]


def test_scopus_and_web_of_science_exports_use_polars_lazy_scan() -> None:
    scopus = ingest_provider_file(FIXTURES / "scopus_export.csv", provider=ProviderName.SCOPUS)
    web_of_science = ingest_provider_file(
        FIXTURES / "web_of_science_export.txt",
        provider=ProviderName.WEB_OF_SCIENCE,
    )

    assert scopus.input_format is InputFormat.CSV
    assert web_of_science.input_format is InputFormat.TSV
    assert scopus.works[0].title == "Scopus Export Fixture"
    assert scopus.works[0].doi == "10.1234/scopus.fixture"
    assert web_of_science.works[0].title == "Web of Science Export Fixture"
    assert web_of_science.works[0].doi == "10.1234/wos.fixture"


def test_scan_tabular_returns_lazy_frame() -> None:
    frame = scan_tabular(FIXTURES / "scopus_export.csv")

    assert isinstance(frame, pl.LazyFrame)
    assert frame.select("Title").collect().item() == "Scopus Export Fixture"


def test_google_scholar_bibtex_export_ingests_without_live_endpoint() -> None:
    spec = DEFAULT_PROVIDER_REGISTRY.get(ProviderName.GOOGLE_SCHOLAR_EXPORT)
    result = ingest_provider_file(FIXTURES / "google_scholar_export.bib", provider=ProviderName.GOOGLE_SCHOLAR_EXPORT)

    assert spec.base_url is None
    assert result.works[0].title == "Google Scholar Export Fixture"
    assert result.works[0].doi == "10.1234/google.fixture"


def test_multi_entry_bibtex_export_returns_one_work_per_entry(tmp_path: Path) -> None:
    path = tmp_path / "google_scholar_export.bib"
    path.write_text(
        """@article{first,
  title = {First Google Scholar Fixture},
  author = {Researcher, One},
  year = {2025},
  doi = {10.1234/google.first}
}

@article{second,
  title = {Second
    Google Scholar Fixture},
  author = {Researcher, Two},
  year = {2026},
  doi = {10.1234/google.second}
}
""",
        encoding="utf-8",
    )

    result = ingest_provider_file(path, provider=ProviderName.GOOGLE_SCHOLAR_EXPORT)

    assert [work.title for work in result.works] == [
        "First Google Scholar Fixture",
        "Second     Google Scholar Fixture",
    ]
    assert [work.doi for work in result.works] == ["10.1234/google.first", "10.1234/google.second"]


def test_ris_export_ingests_for_credential_gated_sources(tmp_path: Path) -> None:
    path = tmp_path / "scopus_export.ris"
    path.write_text(
        """TY  - JOUR
TI  - Scopus RIS Fixture
AU  - Researcher, Example
PY  - 2026
DO  - 10.1234/scopus.ris
ER  -
""",
        encoding="utf-8",
    )

    result = ingest_provider_file(path, provider=ProviderName.SCOPUS)

    assert result.input_format is InputFormat.RIS
    assert result.works[0].title == "Scopus RIS Fixture"
    assert result.works[0].doi == "10.1234/scopus.ris"


def test_preprint_sources_keep_preprint_work_type() -> None:
    arxiv = ingest_provider_file(FIXTURES / "arxiv.json", provider=ProviderName.ARXIV)
    biorxiv = ingest_provider_file(FIXTURES / "biorxiv.json", provider=ProviderName.BIORXIV)

    assert arxiv.works[0].ontology.work_type is WorkType.PREPRINT
    assert biorxiv.works[0].ontology.work_type is WorkType.PREPRINT


@pytest.mark.parametrize(
    ("input_format", "provider"),
    [
        (InputFormat.JSON, ProviderName.OPENALEX),
        (InputFormat.CSV, ProviderName.SCOPUS),
        (InputFormat.TSV, ProviderName.WEB_OF_SCIENCE),
        (InputFormat.BIBTEX, ProviderName.GOOGLE_SCHOLAR_EXPORT),
    ],
)
def test_normalized_works_include_compatibility_metadata(input_format: InputFormat, provider: ProviderName) -> None:
    assert_compatibility_metadata(input_format, provider)


def test_unsupported_provider_format_combinations_fail_closed() -> None:
    with pytest.raises(IngestionError, match="does not support"):
        ingest_provider_file(
            FIXTURES / "openalex.json",
            provider=ProviderName.OPENALEX,
            input_format=InputFormat.CSV,
        )

    with pytest.raises(IngestionError, match="requires configured credentials"):
        ingest_provider_file(
            FIXTURES / "scopus_export.csv",
            provider=ProviderName.SCOPUS,
            input_format=InputFormat.JSON,
        )


def test_text_exports_fail_closed_without_known_tabular_shape(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("not a recognized tabular export\n", encoding="utf-8")

    with pytest.raises(IngestionError, match="cannot infer"):
        ingest_provider_file(path, provider=ProviderName.WEB_OF_SCIENCE)
