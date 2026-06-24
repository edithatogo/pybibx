from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Any, cast

from pydantic import Field, field_validator, model_validator

from pybibx.schemas.enums import CitationIntent, PublicationStatus, WorkType
from pybibx.schemas.records import StrictSchemaModel, normalize_doi, normalize_orcid, normalize_ror
from pybibx.versioning import CompatibilityProfile, VersionedSurface, VersionStamp


class OntologyNamespace(StrEnum):
    SCHEMA_ORG = "schema"
    CITO = "cito"
    FABIO = "fabio"
    FRAPO = "frapo"
    PSO = "pso"
    ORG = "org"
    ROR = "ror"
    ORCID = "orcid"
    CSL = "csl"


NAMESPACE_IRIS: dict[OntologyNamespace, str] = {
    OntologyNamespace.SCHEMA_ORG: "https://schema.org/",
    OntologyNamespace.CITO: "http://purl.org/spar/cito/",
    OntologyNamespace.FABIO: "http://purl.org/spar/fabio/",
    OntologyNamespace.FRAPO: "http://purl.org/cerif/frapo/",
    OntologyNamespace.PSO: "http://purl.org/spar/pso/",
    OntologyNamespace.ORG: "http://www.w3.org/ns/org#",
    OntologyNamespace.ROR: "https://ror.org/",
    OntologyNamespace.ORCID: "https://orcid.org/",
    OntologyNamespace.CSL: "https://citeproc-js.readthedocs.io/en/latest/csl-json/markup.html#",
}


def default_ontology_compatibility_profile() -> CompatibilityProfile:
    return CompatibilityProfile(
        ontology=tuple(
            VersionStamp(surface=VersionedSurface.ONTOLOGY, name=namespace.value, version="2026-06-24")
            for namespace in OntologyNamespace
        ),
    )


class OntologyTerm(StrictSchemaModel):
    namespace: OntologyNamespace
    term: str = Field(min_length=1)
    label: str | None = None
    iri: str | None = None

    @property
    def prefixed_id(self) -> str:
        return f"{self.namespace.value}:{self.term}"

    @model_validator(mode="before")
    @classmethod
    def default_iri(cls, data: object) -> object:
        if not isinstance(data, Mapping):
            return data
        raw_mapping = cast("Mapping[object, object]", data)
        raw: dict[str, object] = {str(key): value for key, value in raw_mapping.items()}
        if raw.get("iri") is not None:
            return raw
        namespace_value = raw["namespace"]
        namespace = (
            namespace_value
            if isinstance(namespace_value, OntologyNamespace)
            else OntologyNamespace(str(namespace_value))
        )
        return {**raw, "iri": f"{NAMESPACE_IRIS[namespace]}{raw['term']}"}


class CitoCitationFacet(StrictSchemaModel):
    source_work_id: str = Field(min_length=1)
    target_work_id: str = Field(min_length=1)
    intent: CitationIntent = CitationIntent.CITES
    context_text: str | None = None
    evidence_ids: tuple[str, ...] = Field(default_factory=tuple)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    @property
    def term(self) -> OntologyTerm:
        namespace, term = self.intent.value.split(":", maxsplit=1)
        return OntologyTerm(namespace=OntologyNamespace(namespace), term=term)


class FabioWorkFacet(StrictSchemaModel):
    work_type: WorkType = WorkType.UNKNOWN
    expression_id: str | None = None
    manifestation_id: str | None = None


class FrapoFundingFacet(StrictSchemaModel):
    funder_id: str | None = None
    funder_name: str | None = None
    grant_number: str | None = None
    project_id: str | None = None


class PsoStatusFacet(StrictSchemaModel):
    publication_status: PublicationStatus = PublicationStatus.PUBLISHED
    status_date: str | None = None


class OrgUnitFacet(StrictSchemaModel):
    name: str = Field(min_length=1)
    ror_id: str | None = None
    parent_ror_id: str | None = None
    role: str | None = None

    @field_validator("ror_id", "parent_ror_id")
    @classmethod
    def validate_ror(cls, value: str | None) -> str | None:
        return normalize_ror(value)


class RorOrganizationFacet(StrictSchemaModel):
    ror_id: str
    name: str = Field(min_length=1)
    country_code: str = Field(min_length=2, max_length=2)
    parent_ror_ids: tuple[str, ...] = Field(default_factory=tuple)
    child_ror_ids: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("ror_id")
    @classmethod
    def validate_ror_id(cls, value: str) -> str:
        normalized = normalize_ror(value)
        if normalized is None:
            msg = "ror_id is required"
            raise ValueError(msg)
        return normalized

    @field_validator("parent_ror_ids", "child_ror_ids")
    @classmethod
    def validate_ror_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(normalize_ror(item) or item for item in value)

    @field_validator("country_code")
    @classmethod
    def normalize_country_code(cls, value: str) -> str:
        return value.upper()


class OrcidIdentityFacet(StrictSchemaModel):
    orcid: str
    display_name: str = Field(min_length=1)
    affiliation_ror_ids: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("orcid")
    @classmethod
    def validate_orcid(cls, value: str) -> str:
        normalized = normalize_orcid(value)
        if normalized is None:
            msg = "orcid is required"
            raise ValueError(msg)
        return normalized

    @field_validator("affiliation_ror_ids")
    @classmethod
    def validate_affiliation_ror_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(normalize_ror(item) or item for item in value)


class CslItem(StrictSchemaModel):
    identifier: str = Field(alias="id", min_length=1)
    item_type: str = Field(alias="type", min_length=1)
    title: str = Field(min_length=1)
    doi: str | None = Field(default=None, alias="DOI")
    issued: dict[str, Any] | None = None
    author: tuple[dict[str, Any], ...] = Field(default_factory=tuple)
    container_title: str | None = Field(default=None, alias="container-title")
    url: str | None = Field(default=None, alias="URL")

    @field_validator("doi")
    @classmethod
    def validate_doi(cls, value: str | None) -> str | None:
        return normalize_doi(value)


class SemanticOntologyBundle(StrictSchemaModel):
    schema_org_type: str = "ScholarlyArticle"
    cito: tuple[CitoCitationFacet, ...] = Field(default_factory=tuple)
    fabio: FabioWorkFacet = Field(default_factory=FabioWorkFacet)
    frapo: tuple[FrapoFundingFacet, ...] = Field(default_factory=tuple)
    pso: PsoStatusFacet = Field(default_factory=PsoStatusFacet)
    org: tuple[OrgUnitFacet, ...] = Field(default_factory=tuple)
    ror: tuple[RorOrganizationFacet, ...] = Field(default_factory=tuple)
    orcid: tuple[OrcidIdentityFacet, ...] = Field(default_factory=tuple)
    csl: CslItem | None = None
    compatibility: CompatibilityProfile = Field(default_factory=default_ontology_compatibility_profile)
