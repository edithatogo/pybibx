"""Regression tests for Polars/Jiter ingestion helpers."""

from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from pybibx.ingestion import IngestionError, ingest_provider_file, load_json_payload, scan_tabular
from pybibx.providers import DEFAULT_PROVIDER_REGISTRY
from pybibx.schemas import InputFormat, ProviderName, WorkType
from pybibx.versioning import VersionedSurface

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "tests" / "fixtures" / "providers"


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


def test_jiter_loader_returns_raw_payload_mapping() -> None:
    payload = load_json_payload(FIXTURES / "openalex.json")

    assert isinstance(payload, dict)
    assert payload["id"] == "https://openalex.org/W123"


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


def test_preprint_sources_keep_preprint_work_type() -> None:
    arxiv = ingest_provider_file(FIXTURES / "arxiv.json", provider=ProviderName.ARXIV)
    biorxiv = ingest_provider_file(FIXTURES / "biorxiv.json", provider=ProviderName.BIORXIV)

    assert arxiv.works[0].ontology.work_type is WorkType.PREPRINT
    assert biorxiv.works[0].ontology.work_type is WorkType.PREPRINT


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
