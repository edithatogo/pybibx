"""Regression tests for provider registry and fixture contracts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from pybibx.providers import (
    DEFAULT_PROVIDER_REGISTRY,
    ProviderAccessMode,
    ProviderCapability,
    ProviderEndpoint,
    ProviderRegistry,
    ProviderSpec,
)
from pybibx.schemas import InputFormat, OutputFormat, ProviderName
from pybibx.settings import PyBibXSettings
from pybibx.versioning import VersionedSurface, VersionStamp

REPO = Path(__file__).resolve().parents[1]
REQUESTED_PROVIDERS = {
    ProviderName.OPENALEX,
    ProviderName.CROSSREF,
    ProviderName.PUBMED,
    ProviderName.MEDLINE,
    ProviderName.OPENCITATIONS,
    ProviderName.SEMANTIC_SCHOLAR,
    ProviderName.ROR,
    ProviderName.ORCID,
    ProviderName.UNPAYWALL,
    ProviderName.ARXIV,
    ProviderName.BIORXIV,
    ProviderName.MEDRXIV,
    ProviderName.GOOGLE_SCHOLAR_EXPORT,
    ProviderName.SCOPUS,
    ProviderName.WEB_OF_SCIENCE,
}


def test_registry_contains_requested_providers() -> None:
    registered = {spec.provider for spec in DEFAULT_PROVIDER_REGISTRY.specs}

    assert registered == REQUESTED_PROVIDERS
    assert (
        DEFAULT_PROVIDER_REGISTRY.get(ProviderName.OPENALEX).endpoint_url("works") == "https://api.openalex.org/works"
    )
    assert (
        DEFAULT_PROVIDER_REGISTRY.get(ProviderName.PUBMED).endpoint_url(
            "search",
        )
        == "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    )
    assert (
        DEFAULT_PROVIDER_REGISTRY.get(ProviderName.OPENCITATIONS).endpoint_url("index")
        == "https://api.opencitations.net/index/v2"
    )


def test_endpoint_response_formats_are_provider_native() -> None:
    endpoint_formats = {
        (spec.provider, endpoint.name): endpoint.response_format
        for spec in DEFAULT_PROVIDER_REGISTRY.specs
        for endpoint in spec.endpoints
    }

    assert endpoint_formats[(ProviderName.OPENALEX, "works")] is InputFormat.JSON
    assert endpoint_formats[(ProviderName.CROSSREF, "works")] is InputFormat.JSON
    assert endpoint_formats[(ProviderName.PUBMED, "fetch")] is InputFormat.XML
    assert endpoint_formats[(ProviderName.OPENCITATIONS, "index")] is InputFormat.JSON
    assert endpoint_formats[(ProviderName.ARXIV, "query")] is InputFormat.XML
    assert all(
        endpoint.output_format is None for spec in DEFAULT_PROVIDER_REGISTRY.specs for endpoint in spec.endpoints
    )


def test_access_modes_preserve_legal_and_credential_boundaries() -> None:
    gated = {spec.provider for spec in DEFAULT_PROVIDER_REGISTRY.credential_gated()}
    export_only = {spec.provider for spec in DEFAULT_PROVIDER_REGISTRY.export_import_only()}

    assert gated == {ProviderName.SCOPUS, ProviderName.WEB_OF_SCIENCE}
    assert export_only == {ProviderName.GOOGLE_SCHOLAR_EXPORT}
    assert DEFAULT_PROVIDER_REGISTRY.get(ProviderName.GOOGLE_SCHOLAR_EXPORT).base_url is None
    assert "do not scrape" in DEFAULT_PROVIDER_REGISTRY.get(ProviderName.GOOGLE_SCHOLAR_EXPORT).terms_note.lower()


def test_registry_capability_queries_are_explicit() -> None:
    preprints = {
        spec.provider for spec in DEFAULT_PROVIDER_REGISTRY.with_capability(ProviderCapability.PREPRINT_SERVER)
    }
    identity = {
        spec.provider for spec in DEFAULT_PROVIDER_REGISTRY.with_capability(ProviderCapability.IDENTITY_REGISTRY)
    }
    full_text = {
        spec.provider for spec in DEFAULT_PROVIDER_REGISTRY.with_capability(ProviderCapability.LEGAL_FULL_TEXT_ROUTER)
    }

    assert preprints == {ProviderName.ARXIV, ProviderName.BIORXIV, ProviderName.MEDRXIV}
    assert {ProviderName.ROR, ProviderName.ORCID}.issubset(identity)
    assert full_text == {ProviderName.UNPAYWALL}


def test_all_registry_fixtures_exist_and_json_fixtures_parse() -> None:
    paths = DEFAULT_PROVIDER_REGISTRY.fixture_paths(root=REPO)

    assert len(paths) == len(REQUESTED_PROVIDERS)
    for path in paths:
        assert path.exists(), path
        if path.suffix == ".json":
            assert json.loads(path.read_text(encoding="utf-8"))
        if path.name == "web_of_science_export.txt":
            web_of_science = DEFAULT_PROVIDER_REGISTRY.get(ProviderName.WEB_OF_SCIENCE)
            assert web_of_science.fixtures[0].input_format is InputFormat.TSV


def test_registry_integrates_with_default_settings() -> None:
    settings = PyBibXSettings()

    for spec in DEFAULT_PROVIDER_REGISTRY.specs:
        provider_settings = settings.provider_settings(spec.provider)
        assert provider_settings is not None, spec.provider
        assert provider_settings.credential_required is spec.credential_required
        assert provider_settings.rate_limit_per_second == spec.rate_limit_per_second
        if spec.access_mode is ProviderAccessMode.CREDENTIAL_GATED:
            assert provider_settings.credential_required is True
            assert provider_settings.enabled is False
        else:
            assert provider_settings.enabled is True


def test_provider_spec_rejects_invalid_boundaries() -> None:
    with pytest.raises(ValidationError, match="credential-gated"):
        ProviderSpec(
            provider=ProviderName.SCOPUS,
            display_name="Bad Scopus",
            access_mode=ProviderAccessMode.CREDENTIAL_GATED,
            capabilities=(ProviderCapability.METADATA_SEARCH,),
            supported_input_formats=(InputFormat.CSV,),
            version=VersionStamp(surface=VersionedSurface.PROVIDER, name="scopus", version="test"),
            terms_note="Credentials are required.",
        )

    with pytest.raises(ValidationError, match="export/import-only"):
        ProviderSpec(
            provider=ProviderName.GOOGLE_SCHOLAR_EXPORT,
            display_name="Bad Google Scholar",
            access_mode=ProviderAccessMode.EXPORT_IMPORT_ONLY,
            base_url="https://scholar.google.com",
            capabilities=(ProviderCapability.EXPORT_IMPORT,),
            supported_input_formats=(InputFormat.BIBTEX,),
            version=VersionStamp(surface=VersionedSurface.PROVIDER, name="google_scholar_export", version="test"),
            terms_note="Exports only.",
        )


def test_provider_registry_rejects_duplicates() -> None:
    spec = ProviderSpec(
        provider=ProviderName.OPENALEX,
        display_name="OpenAlex",
        access_mode=ProviderAccessMode.OPEN_API,
        base_url="https://api.openalex.org",
        capabilities=(ProviderCapability.METADATA_SEARCH,),
        supported_input_formats=(InputFormat.JSON,),
        supported_output_formats=(OutputFormat.JSONL,),
        endpoints=(ProviderEndpoint(name="works", path="/works"),),
        version=VersionStamp(surface=VersionedSurface.PROVIDER, name="openalex", version="test"),
        terms_note="Test provider.",
    )

    with pytest.raises(ValidationError, match="duplicate"):
        ProviderRegistry(specs=(spec, spec))
