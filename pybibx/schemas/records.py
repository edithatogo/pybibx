from __future__ import annotations

import re
from datetime import UTC, date, datetime
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from pybibx.schemas.enums import (
    CitationIntent,
    ExportProfile,
    InputFormat,
    OutputFormat,
    ProviderName,
    PublicationStatus,
    WorkType,
)
from pybibx.versioning import CompatibilityProfile, VersionStamp, default_compatibility_profile

DOI_RE = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)
ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$", re.IGNORECASE)
ROR_RE = re.compile(r"^https://ror\.org/0[a-hj-km-np-tv-z0-9]{7}\d$", re.IGNORECASE)
COUNTRY_RE = re.compile(r"^[A-Z]{2}$")
ORCID_MODULUS = 11
ORCID_CHECK_DIGIT_BASE = 12
ORCID_X_VALUE = 10


class StrictSchemaModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


def normalize_doi(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    if stripped.lower().startswith("https://doi.org/"):
        stripped = stripped[len("https://doi.org/") :]
    if stripped.lower().startswith("doi:"):
        stripped = stripped[4:]
    if not DOI_RE.fullmatch(stripped):
        msg = "DOI must match a Crossref-style 10.x prefix"
        raise ValueError(msg)
    return stripped.lower()


def normalize_orcid(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    if stripped.lower().startswith("https://orcid.org/"):
        stripped = stripped[len("https://orcid.org/") :]
    if not ORCID_RE.fullmatch(stripped):
        msg = "ORCID must be a bare ORCID or https://orcid.org/ URL"
        raise ValueError(msg)
    digits = stripped.replace("-", "").upper()
    total = 0
    for digit in digits[:-1]:
        total = (total + int(digit)) * 2
    remainder = total % ORCID_MODULUS
    result = (ORCID_CHECK_DIGIT_BASE - remainder) % ORCID_MODULUS
    expected_check_digit = "X" if result == ORCID_X_VALUE else str(result)
    if digits[-1] != expected_check_digit:
        msg = "ORCID check digit is invalid"
        raise ValueError(msg)
    return f"https://orcid.org/{stripped.upper()}"


def normalize_ror(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    if not ROR_RE.fullmatch(stripped):
        msg = "ROR ID must be a https://ror.org/ URL"
        raise ValueError(msg)
    return stripped.lower()


class Author(StrictSchemaModel):
    display_name: str = Field(min_length=1)
    orcid: str | None = None
    raw_name: str | None = None
    affiliations: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("orcid")
    @classmethod
    def validate_orcid(cls, value: str | None) -> str | None:
        return normalize_orcid(value)


class Institution(StrictSchemaModel):
    display_name: str = Field(min_length=1)
    ror_id: str | None = None
    country_code: str = Field(min_length=2, max_length=2)
    parent_ror_id: str | None = None

    @field_validator("country_code")
    @classmethod
    def normalize_country_code(cls, value: str) -> str:
        normalized = value.upper()
        if not COUNTRY_RE.fullmatch(normalized):
            msg = "country_code must be an ISO 3166-1 alpha-2 code"
            raise ValueError(msg)
        return normalized

    @field_validator("ror_id", "parent_ror_id")
    @classmethod
    def validate_ror(cls, value: str | None) -> str | None:
        return normalize_ror(value)


class OntologyFacet(StrictSchemaModel):
    work_type: WorkType = WorkType.UNKNOWN
    publication_status: PublicationStatus = PublicationStatus.PUBLISHED
    citation_intents: tuple[CitationIntent, ...] = Field(default_factory=tuple)
    schema_org_type: str = "ScholarlyArticle"
    frapo_funder_id: str | None = None
    grant_number: str | None = None
    org_ror_ids: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("org_ror_ids")
    @classmethod
    def validate_org_ror_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(normalize_ror(item) or item for item in value)


class Work(StrictSchemaModel):
    work_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    doi: str | None = None
    publication_year: int | None = Field(default=None, ge=1000, le=9999)
    publication_date: date | None = None
    authors: tuple[Author, ...] = Field(default_factory=tuple)
    institutions: tuple[Institution, ...] = Field(default_factory=tuple)
    concepts: tuple[str, ...] = Field(default_factory=tuple)
    sustainable_development_goals: tuple[str, ...] = Field(default_factory=tuple)
    citation_count: int = Field(default=0, ge=0)
    source_provider: ProviderName | None = None
    ontology: OntologyFacet = Field(default_factory=OntologyFacet)
    compatibility: CompatibilityProfile = Field(default_factory=default_compatibility_profile)

    @field_validator("doi")
    @classmethod
    def validate_doi(cls, value: str | None) -> str | None:
        return normalize_doi(value)

    @model_validator(mode="after")
    def publication_year_matches_date(self) -> Self:
        if (
            self.publication_date is not None
            and self.publication_year is not None
            and self.publication_date.year != self.publication_year
        ):
            msg = "publication_year must match publication_date.year"
            raise ValueError(msg)
        return self


class Citation(StrictSchemaModel):
    source_work_id: str = Field(min_length=1)
    target_work_id: str = Field(min_length=1)
    source_doi: str | None = None
    target_doi: str | None = None
    intent: CitationIntent = CitationIntent.CITES
    context_text: str | None = None
    evidence_ids: tuple[str, ...] = Field(default_factory=tuple)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    compatibility: CompatibilityProfile = Field(default_factory=default_compatibility_profile)

    @field_validator("source_doi", "target_doi")
    @classmethod
    def validate_doi(cls, value: str | None) -> str | None:
        return normalize_doi(value)


class EvidenceItem(StrictSchemaModel):
    evidence_id: str = Field(min_length=1)
    source_provider: ProviderName
    source_locator: str = Field(min_length=1)
    quote: str | None = None
    context_text: str | None = None
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source_version: VersionStamp | None = None


class EvidenceSet(StrictSchemaModel):
    evidence_set_id: str = Field(min_length=1)
    claim_text: str = Field(min_length=1)
    items: tuple[EvidenceItem, ...] = Field(min_length=1)
    supporting_item_ids: tuple[str, ...] = Field(min_length=1)
    compatibility: CompatibilityProfile = Field(default_factory=default_compatibility_profile)

    @model_validator(mode="after")
    def supporting_items_exist(self) -> Self:
        item_ids = {item.evidence_id for item in self.items}
        missing = set(self.supporting_item_ids) - item_ids
        if missing:
            msg = f"supporting_item_ids not present in items: {sorted(missing)}"
            raise ValueError(msg)
        return self


class ExportManifest(StrictSchemaModel):
    export_id: str = Field(min_length=1)
    export_profile: ExportProfile
    output_format: OutputFormat
    record_count: int = Field(ge=0)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    input_format: InputFormat | None = None
    schema_uri: str | None = None
    evidence_set_ids: tuple[str, ...] = Field(default_factory=tuple)
    compatibility: CompatibilityProfile = Field(default_factory=default_compatibility_profile)

    @model_validator(mode="after")
    def output_profile_matches_format(self) -> Self:
        if self.export_profile is ExportProfile.CSL_BIBLIOGRAPHY and self.output_format is not OutputFormat.CSL_JSON:
            msg = "CSL bibliography exports must use CSL-JSON output"
            raise ValueError(msg)
        return self


def model_json_schema_snapshot(model: type[BaseModel]) -> dict[str, Any]:
    return model.model_json_schema(mode="validation")
