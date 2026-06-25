"""Release-readiness contracts for the maintained PyBibX 6.0 alpha boundary."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from pybibx.schemas.records import StrictSchemaModel


class ReleaseSurfaceKind(StrEnum):
    PUBLIC = "public"
    PROVISIONAL = "provisional"
    OPTIONAL = "optional"
    LEGACY = "legacy"
    INTERNAL = "internal"


class ExtraCompatibilityKind(StrEnum):
    BASELINE_SAFE = "baseline-safe"
    OPTIONAL_SAFE = "optional-safe"
    PROBING_ONLY = "probing-only"
    CREDENTIAL_GATED = "credential-gated"
    BLOCKED = "blocked"


class ReleaseSurfaceItem(StrictSchemaModel):
    module: str = Field(min_length=1)
    kind: ReleaseSurfaceKind
    exports: tuple[str, ...] = Field(default_factory=tuple)
    stability_note: str = Field(min_length=1)

    @model_validator(mode="after")
    def public_surfaces_export_names(self) -> ReleaseSurfaceItem:
        if self.kind in {ReleaseSurfaceKind.PUBLIC, ReleaseSurfaceKind.PROVISIONAL} and not self.exports:
            msg = f"{self.module} must declare exports for its release surface"
            raise ValueError(msg)
        return self


class ExtraCompatibilityItem(StrictSchemaModel):
    extra: str = Field(min_length=1)
    kind: ExtraCompatibilityKind
    install_command: str = Field(min_length=1)
    baseline: bool = False
    note: str = Field(min_length=1)


class ReleaseReadinessContract(StrictSchemaModel):
    release_label: str = "PyBibX 6.0 alpha"
    package_version: str = "5.9.2"
    surfaces: tuple[ReleaseSurfaceItem, ...]
    extras: tuple[ExtraCompatibilityItem, ...]
    local_quality_gates: tuple[str, ...]
    external_gates: tuple[str, ...]

    @model_validator(mode="after")
    def exactly_one_baseline_extra(self) -> ReleaseReadinessContract:
        baselines = [item for item in self.extras if item.baseline]
        if len(baselines) != 1:
            msg = "release readiness must define exactly one baseline install path"
            raise ValueError(msg)
        if baselines[0].kind is not ExtraCompatibilityKind.BASELINE_SAFE:
            msg = "baseline install path must be marked baseline-safe"
            raise ValueError(msg)
        return self


RELEASE_SURFACE: tuple[ReleaseSurfaceItem, ...] = (
    ReleaseSurfaceItem(
        module="pybibx",
        kind=ReleaseSurfaceKind.LEGACY,
        exports=("bibliometrix", "pbx_probe", "web_app", "web_stop"),
        stability_note="PyBibX 5.9.2 compatibility boundary; import remains lazy for legacy runtime dependencies.",
    ),
    ReleaseSurfaceItem(
        module="pybibx.schemas",
        kind=ReleaseSurfaceKind.PUBLIC,
        exports=(
            "Author",
            "Citation",
            "EvidenceSet",
            "ExportManifest",
            "Institution",
            "Work",
        ),
        stability_note="Versioned Pydantic v2 records for maintained normalized data.",
    ),
    ReleaseSurfaceItem(
        module="pybibx.settings",
        kind=ReleaseSurfaceKind.PUBLIC,
        exports=("PyBibXSettings",),
        stability_note="Pydantic-settings entry point for local provider, quality, AI, and RAG configuration.",
    ),
    ReleaseSurfaceItem(
        module="pybibx.providers",
        kind=ReleaseSurfaceKind.PUBLIC,
        exports=("DEFAULT_PROVIDER_REGISTRY", "ProviderRegistry", "ProviderSpec"),
        stability_note="Provider registry metadata, including open, export-only, and credential-gated providers.",
    ),
    ReleaseSurfaceItem(
        module="pybibx.pipeline",
        kind=ReleaseSurfaceKind.PUBLIC,
        exports=("ProviderPipelineRequest", "ProviderPipelineResult", "run_provider_pipeline"),
        stability_note="Offline provider pipeline over local fixtures and exports.",
    ),
    ReleaseSurfaceItem(
        module="pybibx.legacy",
        kind=ReleaseSurfaceKind.PUBLIC,
        exports=("legacy_dataframe_to_works", "legacy_dataframe_to_citations", "works_to_legacy_dataframe"),
        stability_note="Compatibility adapters between maintained schemas and the legacy pandas runtime.",
    ),
    ReleaseSurfaceItem(
        module="pybibx.graph",
        kind=ReleaseSurfaceKind.PROVISIONAL,
        exports=("build_citation_graph", "build_coauthorship_graph", "to_networkx"),
        stability_note="RustWorkX-first graph builders with NetworkX export compatibility.",
    ),
    ReleaseSurfaceItem(
        module="pybibx.ingestion",
        kind=ReleaseSurfaceKind.PROVISIONAL,
        exports=("ingest_provider_file", "scan_jsonl", "scan_tabular"),
        stability_note="Polars/Jiter ingestion helpers that do not replace legacy importers yet.",
    ),
    ReleaseSurfaceItem(
        module="pybibx.rag",
        kind=ReleaseSurfaceKind.OPTIONAL,
        exports=("plan_local_rag_pipeline", "route_unpaywall_full_text", "evaluate_pdf_parsers"),
        stability_note="Local full-text RAG planning contracts; optional Docling/FastEmbed/LanceDB integrations.",
    ),
    ReleaseSurfaceItem(
        module="pybibx.ai",
        kind=ReleaseSurfaceKind.OPTIONAL,
        exports=("default_agent_orchestration_plan", "build_local_runtime", "create_instructor_extraction_spec"),
        stability_note=(
            "AI orchestration contracts for optional PydanticAI, Instructor, DSPy, LlamaIndex, and local runtimes."
        ),
    ),
    ReleaseSurfaceItem(
        module="pybibx.reports",
        kind=ReleaseSurfaceKind.PROVISIONAL,
        exports=("build_citation_safe_report", "build_biblib_markdown_notes", "export_csl_json"),
        stability_note="Citation-safe report and export planning contracts; UI runtimes remain optional.",
    ),
    ReleaseSurfaceItem(
        module="pybibx.quality",
        kind=ReleaseSurfaceKind.PROVISIONAL,
        exports=("build_default_quality_observability_plan", "build_pytest_gremlins_spec", "build_scalene_profile"),
        stability_note="Quality, observability, and profiling plan contracts; heavyweight tools remain optional.",
    ),
    ReleaseSurfaceItem(
        module="pybibx.base",
        kind=ReleaseSurfaceKind.LEGACY,
        exports=("pbx_probe",),
        stability_note="Legacy analysis engine remains supported but excluded from strict 6.0 type/lint gates.",
    ),
)

EXTRA_COMPATIBILITY: tuple[ExtraCompatibilityItem, ...] = (
    ExtraCompatibilityItem(
        extra="baseline",
        kind=ExtraCompatibilityKind.BASELINE_SAFE,
        install_command="uv sync --group dev",
        baseline=True,
        note="CI-supported Python 3.14 path for maintained package code and developer tools.",
    ),
    ExtraCompatibilityItem(
        extra="legacy",
        kind=ExtraCompatibilityKind.PROBING_ONLY,
        install_command="uv sync --extra legacy --group dev",
        note="Legacy NLP/UI stack; not baseline-safe while Python 3.14 compatibility remains unresolved.",
    ),
    ExtraCompatibilityItem(
        extra="quality",
        kind=ExtraCompatibilityKind.OPTIONAL_SAFE,
        install_command="uv sync --extra quality --group dev",
        note="Great Expectations, Deepchecks, and Kedro planning lane.",
    ),
    ExtraCompatibilityItem(
        extra="ai",
        kind=ExtraCompatibilityKind.OPTIONAL_SAFE,
        install_command="uv sync --extra ai --group dev",
        note="PydanticAI, Instructor, DSPy, LlamaIndex, and hosted client adapters remain optional.",
    ),
    ExtraCompatibilityItem(
        extra="rag",
        kind=ExtraCompatibilityKind.OPTIONAL_SAFE,
        install_command="uv sync --extra rag --group dev",
        note="Docling, FastEmbed, and LanceDB local full-text planning lane.",
    ),
    ExtraCompatibilityItem(
        extra="ui",
        kind=ExtraCompatibilityKind.PROBING_ONLY,
        install_command="uv sync --extra ui --group dev",
        note="Reflex is present for evaluation; hosted UI product readiness is not claimed.",
    ),
    ExtraCompatibilityItem(
        extra="reports",
        kind=ExtraCompatibilityKind.OPTIONAL_SAFE,
        install_command="uv sync --extra reports --group dev",
        note="No additional dependency today; marks report/export surface intent.",
    ),
    ExtraCompatibilityItem(
        extra="all",
        kind=ExtraCompatibilityKind.BLOCKED,
        install_command="uv sync --all-extras --group dev",
        note="Not baseline-safe on Python 3.14 while legacy NLP dependencies can fail to build.",
    ),
)

LOCAL_QUALITY_GATES: tuple[str, ...] = (
    "uv lock --check",
    "uv run --group dev pytest tests -q",
    "uv run --group dev ruff check pybibx setup.py tests",
    "uv run --group dev ruff format --check pybibx setup.py tests",
    "uv run --group dev pyright",
    "uv run --group dev ty check pybibx/__init__.py pybibx/release.py",
    "uv run --group dev python -m build --wheel",
    "vale docs conductor README.md",
)

EXTERNAL_RELEASE_GATES: tuple[str, ...] = (
    "PyPI publishing and tag creation require explicit user instruction.",
    "Credential-gated Scopus and Web of Science connectors require user credentials.",
    "Cline with deepseek-v4-flash remains blocked in this non-TTY session.",
    "Hosted LLMs, Reflex, Cosmograph, Rig, Graphina, PyG, PDFMux, and Monty are not production claims.",
)


def release_readiness_contract() -> ReleaseReadinessContract:
    return ReleaseReadinessContract(
        surfaces=RELEASE_SURFACE,
        extras=EXTRA_COMPATIBILITY,
        local_quality_gates=LOCAL_QUALITY_GATES,
        external_gates=EXTERNAL_RELEASE_GATES,
    )


__all__ = [
    "EXTERNAL_RELEASE_GATES",
    "EXTRA_COMPATIBILITY",
    "LOCAL_QUALITY_GATES",
    "RELEASE_SURFACE",
    "ExtraCompatibilityItem",
    "ExtraCompatibilityKind",
    "ReleaseReadinessContract",
    "ReleaseSurfaceItem",
    "ReleaseSurfaceKind",
    "release_readiness_contract",
]
