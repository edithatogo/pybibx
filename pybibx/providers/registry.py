from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Self

from pydantic import Field, model_validator

from pybibx.schemas.enums import InputFormat, OutputFormat, ProviderName
from pybibx.schemas.records import StrictSchemaModel
from pybibx.versioning import VersionedSurface, VersionStamp

if TYPE_CHECKING:
    from pybibx.settings import PyBibXSettings


class ProviderAccessMode(StrEnum):
    OPEN_API = "open-api"
    CREDENTIAL_GATED = "credential-gated"
    EXPORT_IMPORT_ONLY = "export-import-only"


class ProviderCapability(StrEnum):
    METADATA_SEARCH = "metadata-search"
    METADATA_LOOKUP = "metadata-lookup"
    BULK_SNAPSHOT = "bulk-snapshot"
    CITATION_INDEX = "citation-index"
    SEMANTIC_CITATIONS = "semantic-citations"
    IDENTITY_REGISTRY = "identity-registry"
    ORGANIZATION_REGISTRY = "organization-registry"
    LEGAL_FULL_TEXT_ROUTER = "legal-full-text-router"
    PREPRINT_SERVER = "preprint-server"
    EXPORT_IMPORT = "export-import"


class ProviderEndpoint(StrictSchemaModel):
    name: str = Field(min_length=1)
    path: str = Field(min_length=1)
    input_format: InputFormat | None = None
    output_format: OutputFormat | None = None
    docs_url: str | None = None


class ProviderFixture(StrictSchemaModel):
    fixture_id: str = Field(min_length=1)
    path: Path
    input_format: InputFormat
    description: str = Field(min_length=1)
    record_count: int = Field(default=1, ge=0)


class ProviderSpec(StrictSchemaModel):
    provider: ProviderName
    display_name: str = Field(min_length=1)
    access_mode: ProviderAccessMode
    base_url: str | None = None
    docs_url: str | None = None
    credential_required: bool = False
    polite_email_required: bool = False
    api_key_env_var: str | None = None
    rate_limit_per_second: float = Field(default=1.0, gt=0)
    capabilities: tuple[ProviderCapability, ...]
    supported_input_formats: tuple[InputFormat, ...]
    supported_output_formats: tuple[OutputFormat, ...] = Field(default_factory=tuple)
    endpoints: tuple[ProviderEndpoint, ...] = Field(default_factory=tuple)
    fixtures: tuple[ProviderFixture, ...] = Field(default_factory=tuple)
    version: VersionStamp
    terms_note: str = Field(min_length=1)

    @model_validator(mode="after")
    def credential_flags_match_access_mode(self) -> Self:
        if self.access_mode is ProviderAccessMode.CREDENTIAL_GATED and not self.credential_required:
            msg = "credential-gated providers must set credential_required"
            raise ValueError(msg)
        if self.access_mode is ProviderAccessMode.EXPORT_IMPORT_ONLY and self.base_url is not None:
            msg = "export/import-only providers must not define a live base_url"
            raise ValueError(msg)
        return self

    def endpoint_url(self, endpoint_name: str) -> str:
        endpoint = next((item for item in self.endpoints if item.name == endpoint_name), None)
        if endpoint is None:
            msg = f"unknown endpoint: {endpoint_name}"
            raise KeyError(msg)
        if self.base_url is None:
            msg = f"provider {self.provider} does not expose live endpoints"
            raise ValueError(msg)
        return f"{self.base_url.rstrip('/')}/{endpoint.path.lstrip('/')}"

    def settings(self, app_settings: PyBibXSettings) -> object | None:
        return app_settings.provider_settings(self.provider)


class ProviderRegistry(StrictSchemaModel):
    specs: tuple[ProviderSpec, ...]

    @model_validator(mode="after")
    def provider_names_are_unique(self) -> Self:
        names = [spec.provider for spec in self.specs]
        if len(names) != len(set(names)):
            msg = "provider registry contains duplicate provider names"
            raise ValueError(msg)
        return self

    def get(self, provider: ProviderName) -> ProviderSpec:
        for spec in self.specs:
            if spec.provider is provider:
                return spec
        msg = f"provider is not registered: {provider}"
        raise KeyError(msg)

    def by_access_mode(self, access_mode: ProviderAccessMode) -> tuple[ProviderSpec, ...]:
        return tuple(spec for spec in self.specs if spec.access_mode is access_mode)

    def with_capability(self, capability: ProviderCapability) -> tuple[ProviderSpec, ...]:
        return tuple(spec for spec in self.specs if capability in spec.capabilities)

    def credential_gated(self) -> tuple[ProviderSpec, ...]:
        return self.by_access_mode(ProviderAccessMode.CREDENTIAL_GATED)

    def export_import_only(self) -> tuple[ProviderSpec, ...]:
        return self.by_access_mode(ProviderAccessMode.EXPORT_IMPORT_ONLY)

    def fixture_paths(self, *, root: Path) -> tuple[Path, ...]:
        return tuple(root / fixture.path for spec in self.specs for fixture in spec.fixtures)


def _version(provider: ProviderName, version: str = "2026-06-24") -> VersionStamp:
    return VersionStamp(surface=VersionedSurface.PROVIDER, name=provider.value, version=version)


def _json_fixture(provider: ProviderName, description: str) -> ProviderFixture:
    return ProviderFixture(
        fixture_id=f"{provider.value}-minimal-json",
        path=Path(f"tests/fixtures/providers/{provider.value}.json"),
        input_format=InputFormat.JSON,
        description=description,
    )


DEFAULT_PROVIDER_REGISTRY = ProviderRegistry(
    specs=(
        ProviderSpec(
            provider=ProviderName.OPENALEX,
            display_name="OpenAlex",
            access_mode=ProviderAccessMode.OPEN_API,
            base_url="https://api.openalex.org",
            docs_url="https://developers.openalex.org/api-reference/introduction",
            api_key_env_var="PYBIBX_OPENALEX_API_KEY",
            rate_limit_per_second=10.0,
            capabilities=(ProviderCapability.METADATA_SEARCH, ProviderCapability.BULK_SNAPSHOT),
            supported_input_formats=(InputFormat.JSON, InputFormat.JSONL),
            supported_output_formats=(OutputFormat.JSONL, OutputFormat.PARQUET),
            endpoints=(
                ProviderEndpoint(name="works", path="/works", output_format=OutputFormat.JSONL),
                ProviderEndpoint(name="authors", path="/authors", output_format=OutputFormat.JSONL),
                ProviderEndpoint(name="institutions", path="/institutions", output_format=OutputFormat.JSONL),
            ),
            fixtures=(_json_fixture(ProviderName.OPENALEX, "Minimal OpenAlex work payload."),),
            version=_version(ProviderName.OPENALEX),
            terms_note="Use official API credentials and pricing/usage terms when required by OpenAlex.",
        ),
        ProviderSpec(
            provider=ProviderName.CROSSREF,
            display_name="Crossref",
            access_mode=ProviderAccessMode.OPEN_API,
            base_url="https://api.crossref.org",
            docs_url="https://www.crossref.org/documentation/retrieve-metadata/rest-api/",
            polite_email_required=True,
            api_key_env_var="PYBIBX_CROSSREF_API_KEY",
            rate_limit_per_second=5.0,
            capabilities=(ProviderCapability.METADATA_SEARCH, ProviderCapability.METADATA_LOOKUP),
            supported_input_formats=(InputFormat.JSON,),
            supported_output_formats=(OutputFormat.JSONL, OutputFormat.PARQUET),
            endpoints=(ProviderEndpoint(name="works", path="/works", output_format=OutputFormat.JSONL),),
            fixtures=(_json_fixture(ProviderName.CROSSREF, "Minimal Crossref work message."),),
            version=_version(ProviderName.CROSSREF),
            terms_note="Prefer polite-pool identification via mailto or agent header; Metadata Plus requires a token.",
        ),
        ProviderSpec(
            provider=ProviderName.PUBMED,
            display_name="PubMed",
            access_mode=ProviderAccessMode.OPEN_API,
            base_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
            docs_url="https://www.ncbi.nlm.nih.gov/books/NBK25500/",
            polite_email_required=True,
            api_key_env_var="PYBIBX_NCBI_API_KEY",
            rate_limit_per_second=3.0,
            capabilities=(ProviderCapability.METADATA_SEARCH, ProviderCapability.METADATA_LOOKUP),
            supported_input_formats=(InputFormat.XML, InputFormat.JSON),
            supported_output_formats=(OutputFormat.JSONL, OutputFormat.PARQUET),
            endpoints=(
                ProviderEndpoint(name="search", path="/esearch.fcgi", output_format=OutputFormat.JSONL),
                ProviderEndpoint(name="summary", path="/esummary.fcgi", output_format=OutputFormat.JSONL),
                ProviderEndpoint(name="fetch", path="/efetch.fcgi", output_format=OutputFormat.JSONL),
            ),
            fixtures=(_json_fixture(ProviderName.PUBMED, "Minimal PubMed E-utilities JSON payload."),),
            version=_version(ProviderName.PUBMED),
            terms_note=(
                "Use NCBI E-utilities etiquette, including tool/email identification and API keys where applicable."
            ),
        ),
        ProviderSpec(
            provider=ProviderName.MEDLINE,
            display_name="MEDLINE",
            access_mode=ProviderAccessMode.OPEN_API,
            base_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
            docs_url="https://www.ncbi.nlm.nih.gov/home/develop/api/",
            polite_email_required=True,
            api_key_env_var="PYBIBX_NCBI_API_KEY",
            rate_limit_per_second=3.0,
            capabilities=(ProviderCapability.METADATA_SEARCH, ProviderCapability.METADATA_LOOKUP),
            supported_input_formats=(InputFormat.XML, InputFormat.JSON),
            supported_output_formats=(OutputFormat.JSONL, OutputFormat.PARQUET),
            endpoints=(ProviderEndpoint(name="fetch", path="/efetch.fcgi", output_format=OutputFormat.JSONL),),
            fixtures=(_json_fixture(ProviderName.MEDLINE, "Minimal MEDLINE/PubMed payload."),),
            version=_version(ProviderName.MEDLINE),
            terms_note="MEDLINE access is routed through NCBI E-utilities in this registry.",
        ),
        ProviderSpec(
            provider=ProviderName.OPENCITATIONS,
            display_name="OpenCitations",
            access_mode=ProviderAccessMode.OPEN_API,
            base_url="https://opencitations.net",
            docs_url="https://opencitations.net/index/api/v2",
            rate_limit_per_second=2.0,
            capabilities=(ProviderCapability.CITATION_INDEX, ProviderCapability.SEMANTIC_CITATIONS),
            supported_input_formats=(InputFormat.JSON,),
            supported_output_formats=(OutputFormat.JSONL, OutputFormat.PARQUET),
            endpoints=(ProviderEndpoint(name="index", path="/index/api/v2", output_format=OutputFormat.JSONL),),
            fixtures=(_json_fixture(ProviderName.OPENCITATIONS, "Minimal OpenCitations citation payload."),),
            version=_version(ProviderName.OPENCITATIONS),
            terms_note="Use OpenCitations APIs and dumps for open citation data; preserve citation provenance.",
        ),
        ProviderSpec(
            provider=ProviderName.SEMANTIC_SCHOLAR,
            display_name="Semantic Scholar",
            access_mode=ProviderAccessMode.OPEN_API,
            base_url="https://api.semanticscholar.org",
            docs_url="https://api.semanticscholar.org/api-docs/",
            api_key_env_var="PYBIBX_SEMANTIC_SCHOLAR_API_KEY",
            rate_limit_per_second=1.0,
            capabilities=(
                ProviderCapability.METADATA_SEARCH,
                ProviderCapability.CITATION_INDEX,
                ProviderCapability.SEMANTIC_CITATIONS,
                ProviderCapability.BULK_SNAPSHOT,
            ),
            supported_input_formats=(InputFormat.JSON,),
            supported_output_formats=(OutputFormat.JSONL, OutputFormat.PARQUET),
            endpoints=(
                ProviderEndpoint(name="graph-paper", path="/graph/v1/paper", output_format=OutputFormat.JSONL),
                ProviderEndpoint(name="datasets", path="/datasets/v1", output_format=OutputFormat.JSONL),
            ),
            fixtures=(_json_fixture(ProviderName.SEMANTIC_SCHOLAR, "Minimal Semantic Scholar paper payload."),),
            version=_version(ProviderName.SEMANTIC_SCHOLAR),
            terms_note="Use Semantic Scholar API key and rate-limit rules where required.",
        ),
        ProviderSpec(
            provider=ProviderName.ROR,
            display_name="Research Organization Registry",
            access_mode=ProviderAccessMode.OPEN_API,
            base_url="https://api.ror.org/v2",
            docs_url="https://ror.readme.io/docs/rest-api",
            rate_limit_per_second=2.0,
            capabilities=(ProviderCapability.ORGANIZATION_REGISTRY, ProviderCapability.IDENTITY_REGISTRY),
            supported_input_formats=(InputFormat.JSON,),
            supported_output_formats=(OutputFormat.JSONL, OutputFormat.PARQUET),
            endpoints=(
                ProviderEndpoint(name="organizations", path="/organizations", output_format=OutputFormat.JSONL),
            ),
            fixtures=(_json_fixture(ProviderName.ROR, "Minimal ROR organization payload."),),
            version=_version(ProviderName.ROR, "v2"),
            terms_note="Use ROR API v2 and schema v2 semantics for organization identity.",
        ),
        ProviderSpec(
            provider=ProviderName.ORCID,
            display_name="ORCID",
            access_mode=ProviderAccessMode.OPEN_API,
            base_url="https://pub.orcid.org/v3.0",
            docs_url="https://info.orcid.org/what-is-orcid/services/public-api/",
            credential_required=True,
            api_key_env_var="PYBIBX_ORCID_ACCESS_TOKEN",
            rate_limit_per_second=1.0,
            capabilities=(ProviderCapability.IDENTITY_REGISTRY, ProviderCapability.METADATA_LOOKUP),
            supported_input_formats=(InputFormat.JSON, InputFormat.XML),
            supported_output_formats=(OutputFormat.JSONL, OutputFormat.PARQUET),
            endpoints=(ProviderEndpoint(name="record", path="/{orcid}/record", output_format=OutputFormat.JSONL),),
            fixtures=(_json_fixture(ProviderName.ORCID, "Minimal ORCID public record payload."),),
            version=_version(ProviderName.ORCID, "3.0"),
            terms_note="ORCID public API access requires registered credentials and access tokens.",
        ),
        ProviderSpec(
            provider=ProviderName.UNPAYWALL,
            display_name="Unpaywall",
            access_mode=ProviderAccessMode.OPEN_API,
            base_url="https://api.unpaywall.org/v2",
            docs_url="https://unpaywall.org/products/api",
            polite_email_required=True,
            rate_limit_per_second=2.0,
            capabilities=(ProviderCapability.LEGAL_FULL_TEXT_ROUTER, ProviderCapability.METADATA_LOOKUP),
            supported_input_formats=(InputFormat.JSON,),
            supported_output_formats=(OutputFormat.JSONL, OutputFormat.PARQUET),
            endpoints=(ProviderEndpoint(name="doi", path="/{doi}", output_format=OutputFormat.JSONL),),
            fixtures=(_json_fixture(ProviderName.UNPAYWALL, "Minimal Unpaywall DOI payload."),),
            version=_version(ProviderName.UNPAYWALL, "v2"),
            terms_note="Every Unpaywall request must include an email parameter; only legal OA links should feed RAG.",
        ),
        ProviderSpec(
            provider=ProviderName.ARXIV,
            display_name="arXiv",
            access_mode=ProviderAccessMode.OPEN_API,
            base_url="https://export.arxiv.org/api",
            docs_url="https://info.arxiv.org/help/api/user-manual.html",
            rate_limit_per_second=0.33,
            capabilities=(ProviderCapability.PREPRINT_SERVER, ProviderCapability.METADATA_SEARCH),
            supported_input_formats=(InputFormat.XML, InputFormat.JSON),
            supported_output_formats=(OutputFormat.JSONL, OutputFormat.PARQUET),
            endpoints=(ProviderEndpoint(name="query", path="/query", output_format=OutputFormat.JSONL),),
            fixtures=(_json_fixture(ProviderName.ARXIV, "Minimal normalized arXiv fixture payload."),),
            version=_version(ProviderName.ARXIV),
            terms_note="Respect arXiv API terms and use bulk data paths for large retrieval.",
        ),
        ProviderSpec(
            provider=ProviderName.BIORXIV,
            display_name="bioRxiv",
            access_mode=ProviderAccessMode.OPEN_API,
            base_url="https://api.biorxiv.org",
            docs_url="https://api.biorxiv.org/",
            rate_limit_per_second=1.0,
            capabilities=(ProviderCapability.PREPRINT_SERVER, ProviderCapability.METADATA_SEARCH),
            supported_input_formats=(InputFormat.JSON,),
            supported_output_formats=(OutputFormat.JSONL, OutputFormat.PARQUET),
            endpoints=(ProviderEndpoint(name="details", path="/details/biorxiv", output_format=OutputFormat.JSONL),),
            fixtures=(_json_fixture(ProviderName.BIORXIV, "Minimal bioRxiv details payload."),),
            version=_version(ProviderName.BIORXIV),
            terms_note="Use official bioRxiv API endpoints and avoid bulk scraping.",
        ),
        ProviderSpec(
            provider=ProviderName.MEDRXIV,
            display_name="medRxiv",
            access_mode=ProviderAccessMode.OPEN_API,
            base_url="https://api.medrxiv.org",
            docs_url="https://api.medrxiv.org/",
            rate_limit_per_second=1.0,
            capabilities=(ProviderCapability.PREPRINT_SERVER, ProviderCapability.METADATA_SEARCH),
            supported_input_formats=(InputFormat.JSON,),
            supported_output_formats=(OutputFormat.JSONL, OutputFormat.PARQUET),
            endpoints=(ProviderEndpoint(name="details", path="/details/medrxiv", output_format=OutputFormat.JSONL),),
            fixtures=(_json_fixture(ProviderName.MEDRXIV, "Minimal medRxiv details payload."),),
            version=_version(ProviderName.MEDRXIV),
            terms_note="Use official medRxiv API endpoints and avoid bulk scraping.",
        ),
        ProviderSpec(
            provider=ProviderName.GOOGLE_SCHOLAR_EXPORT,
            display_name="Google Scholar export",
            access_mode=ProviderAccessMode.EXPORT_IMPORT_ONLY,
            docs_url="https://scholar.google.com",
            rate_limit_per_second=1.0,
            capabilities=(ProviderCapability.EXPORT_IMPORT,),
            supported_input_formats=(InputFormat.BIBTEX, InputFormat.CSV),
            supported_output_formats=(OutputFormat.JSONL, OutputFormat.PARQUET),
            fixtures=(
                ProviderFixture(
                    fixture_id="google-scholar-export-bibtex",
                    path=Path("tests/fixtures/providers/google_scholar_export.bib"),
                    input_format=InputFormat.BIBTEX,
                    description="Minimal Google Scholar BibTeX export fixture.",
                ),
            ),
            version=_version(ProviderName.GOOGLE_SCHOLAR_EXPORT),
            terms_note="Import user-provided exports only; do not scrape Google Scholar.",
        ),
        ProviderSpec(
            provider=ProviderName.SCOPUS,
            display_name="Scopus",
            access_mode=ProviderAccessMode.CREDENTIAL_GATED,
            docs_url="https://www.elsevier.com/products/scopus",
            credential_required=True,
            api_key_env_var="PYBIBX_SCOPUS_API_KEY",
            capabilities=(ProviderCapability.METADATA_SEARCH, ProviderCapability.CITATION_INDEX),
            supported_input_formats=(InputFormat.CSV, InputFormat.RIS, InputFormat.BIBTEX),
            supported_output_formats=(OutputFormat.JSONL, OutputFormat.PARQUET),
            fixtures=(
                ProviderFixture(
                    fixture_id="scopus-export-csv",
                    path=Path("tests/fixtures/providers/scopus_export.csv"),
                    input_format=InputFormat.CSV,
                    description="Minimal user-provided Scopus CSV export fixture.",
                ),
            ),
            version=_version(ProviderName.SCOPUS),
            terms_note="Credential/license-gated; support user exports and configured institutional API access only.",
        ),
        ProviderSpec(
            provider=ProviderName.WEB_OF_SCIENCE,
            display_name="Web of Science",
            access_mode=ProviderAccessMode.CREDENTIAL_GATED,
            docs_url="https://clarivate.com/academia-government/scientific-and-academic-research/research-discovery-and-referencing/web-of-science/",
            credential_required=True,
            api_key_env_var="PYBIBX_WEB_OF_SCIENCE_API_KEY",
            capabilities=(ProviderCapability.METADATA_SEARCH, ProviderCapability.CITATION_INDEX),
            supported_input_formats=(InputFormat.CSV, InputFormat.RIS, InputFormat.BIBTEX),
            supported_output_formats=(OutputFormat.JSONL, OutputFormat.PARQUET),
            fixtures=(
                ProviderFixture(
                    fixture_id="web-of-science-export-tab",
                    path=Path("tests/fixtures/providers/web_of_science_export.txt"),
                    input_format=InputFormat.CSV,
                    description="Minimal user-provided Web of Science tabular export fixture.",
                ),
            ),
            version=_version(ProviderName.WEB_OF_SCIENCE),
            terms_note="Credential/license-gated; support user exports and configured institutional API access only.",
        ),
    ),
)


def provider_registry() -> ProviderRegistry:
    return DEFAULT_PROVIDER_REGISTRY
