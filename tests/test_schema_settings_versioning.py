"""Regression tests for maintained schema, settings, and version profiles."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from pybibx.schemas import (
    Author,
    Citation,
    CitationIntent,
    EvidenceItem,
    EvidenceSet,
    ExportManifest,
    ExportProfile,
    Institution,
    OutputFormat,
    ProviderName,
    Work,
    WorkType,
    model_json_schema_snapshot,
)
from pybibx.settings import ProviderSettings, PyBibXSettings, load_settings, settings_version_stamp
from pybibx.versioning import CompatibilityProfile, VersionedSurface, VersionStamp, default_compatibility_profile


def test_work_model_normalizes_identifiers_and_versions() -> None:
    work = Work(
        work_id="openalex:W123",
        title="A checked bibliometric record",
        doi="https://doi.org/10.1234/ABC.DEF",
        publication_year=2026,
        publication_date=date(2026, 1, 2),
        authors=(Author(display_name="Ada Lovelace", orcid="0000-0002-1825-0097"),),
        institutions=(
            Institution(
                display_name="Example University",
                ror_id="https://ror.org/03yrm5c26",
                country_code="nz",
            ),
        ),
        concepts=("bibliometrics",),
        sustainable_development_goals=("SDG 9",),
        citation_count=12,
        source_provider=ProviderName.OPENALEX,
    )

    assert work.doi == "10.1234/abc.def"
    assert work.authors[0].orcid == "https://orcid.org/0000-0002-1825-0097"
    assert work.institutions[0].country_code == "NZ"
    assert work.compatibility.library.name == "pybibx"


def test_invalid_work_constraints_fail_closed() -> None:
    with pytest.raises(ValidationError, match="DOI"):
        Work(work_id="bad", title="Bad DOI", doi="not-a-doi")

    with pytest.raises(ValidationError, match="publication_year"):
        Work(
            work_id="year-mismatch",
            title="Year mismatch",
            publication_year=2025,
            publication_date=date(2026, 1, 1),
        )

    with pytest.raises(ValidationError, match="country_code"):
        Institution(display_name="No Country", country_code="ZZZ")


def test_citation_evidence_and_export_models_validate_semantic_boundaries() -> None:
    citation = Citation(
        source_work_id="W1",
        target_work_id="W2",
        source_doi="doi:10.5555/SOURCE",
        target_doi="10.5555/TARGET",
        intent=CitationIntent.REFUTES,
        evidence_ids=("e1",),
        confidence=0.8,
    )
    evidence_item = EvidenceItem(
        evidence_id="e1",
        source_provider=ProviderName.UNPAYWALL,
        source_locator="https://example.test/fulltext.pdf#page=4",
        quote="Contradictory result sentence.",
    )
    evidence_set = EvidenceSet(
        evidence_set_id="set1",
        claim_text="The citation refutes the target claim.",
        items=(evidence_item,),
        supporting_item_ids=citation.evidence_ids,
    )
    manifest = ExportManifest(
        export_id="export1",
        export_profile=ExportProfile.CSL_BIBLIOGRAPHY,
        output_format=OutputFormat.CSL_JSON,
        record_count=1,
        evidence_set_ids=(evidence_set.evidence_set_id,),
    )

    assert citation.source_doi == "10.5555/source"
    assert evidence_set.supporting_item_ids == ("e1",)
    assert manifest.output_format is OutputFormat.CSL_JSON

    with pytest.raises(ValidationError, match="supporting_item_ids"):
        EvidenceSet(
            evidence_set_id="set2",
            claim_text="Unsupported claim",
            items=(evidence_item,),
            supporting_item_ids=("missing",),
        )

    with pytest.raises(ValidationError, match="CSL bibliography"):
        ExportManifest(
            export_id="export2",
            export_profile=ExportProfile.CSL_BIBLIOGRAPHY,
            output_format=OutputFormat.JSONL,
            record_count=1,
        )


def test_version_profiles_and_schema_snapshots_are_explicit() -> None:
    provider = VersionStamp(surface=VersionedSurface.PROVIDER, name="openalex", version="2026-06-24")
    profile = CompatibilityProfile(provider=provider)
    snapshot = model_json_schema_snapshot(Work)

    assert profile.provider == provider
    assert default_compatibility_profile().schema_profile.version == "1.0.0"
    assert snapshot["title"] == "Work"
    assert snapshot["additionalProperties"] is False


def test_settings_defaults_and_environment_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYBIBX_RUNTIME__DEFAULT_MODEL", "local-bibliometrics")
    monkeypatch.setenv("PYBIBX_FEATURES__ENABLE_HOSTED_LLMS", "true")
    monkeypatch.setenv("PYBIBX_OBSERVABILITY__LOG_LEVEL", "DEBUG")

    settings = load_settings()
    openalex = settings.provider_settings(ProviderName.OPENALEX)
    scopus = settings.provider_settings(ProviderName.SCOPUS)

    assert settings.runtime.default_model == "local-bibliometrics"
    assert settings.features.enable_hosted_llms is True
    assert settings.observability.log_level == "DEBUG"
    assert settings.observability.loguru_enabled is True
    assert settings.quality.great_expectations_enabled is True
    assert settings.quality.pytest_gremlins_enabled is True
    assert settings.ui_reports.citation_safe_reports_enabled is True
    assert settings.ui_reports.reflex_enabled is False
    assert openalex is not None
    assert openalex.enabled is True
    assert scopus is not None
    assert scopus.credential_required is True
    assert settings_version_stamp().surface is VersionedSurface.SETTINGS


def test_provider_settings_validate_rate_limits_and_secret_boundaries() -> None:
    provider = ProviderSettings(provider=ProviderName.CROSSREF, api_key="secret", rate_limit_per_second=2.5)

    assert provider.api_key is not None
    assert provider.api_key.get_secret_value() == "secret"

    with pytest.raises(ValidationError, match="greater than 0"):
        PyBibXSettings(
            providers=(ProviderSettings(provider=ProviderName.OPENALEX, rate_limit_per_second=0),),
        )


def test_work_type_enum_preserves_ontology_values() -> None:
    assert WorkType.JOURNAL_ARTICLE.value == "fabio:JournalArticle"
