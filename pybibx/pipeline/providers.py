from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Self

from pydantic import Field, model_validator

from pybibx.ingestion import IngestionError, IngestionResult, ingest_provider_file
from pybibx.providers import DEFAULT_PROVIDER_REGISTRY, ProviderAccessMode, ProviderRegistry, ProviderSpec
from pybibx.reports import export_csl_json
from pybibx.schemas import ExportManifest, ExportProfile, InputFormat, OutputFormat, ProviderName, Work
from pybibx.schemas.records import StrictSchemaModel
from pybibx.settings import PyBibXSettings, load_settings
from pybibx.versioning import CompatibilityProfile, VersionedSurface, VersionStamp


class PipelineError(ValueError):
    pass


class PipelineOutputFormat(StrEnum):
    JSONL = "jsonl"
    CSL_JSON = "csl-json"

    def to_output_format(self) -> OutputFormat:
        if self is PipelineOutputFormat.JSONL:
            return OutputFormat.JSONL
        if self is PipelineOutputFormat.CSL_JSON:
            return OutputFormat.CSL_JSON
        msg = f"unsupported pipeline output format: {self.value}"
        raise PipelineError(msg)


class ProviderPipelineSource(StrictSchemaModel):
    provider: ProviderName
    source_path: Path
    input_format: InputFormat
    provider_version: VersionStamp
    input_version: VersionStamp
    access_mode: ProviderAccessMode
    terms_note: str = Field(min_length=1)


class ProviderPipelineRawRecord(StrictSchemaModel):
    provider: ProviderName
    source_path: Path
    input_format: InputFormat
    content_digest: Annotated[str, Field(pattern=r"^sha256:[0-9a-f]{64}$")]
    byte_count: int = Field(ge=0)
    provider_version: VersionStamp
    input_version: VersionStamp


class ProviderPipelineRequest(StrictSchemaModel):
    inputs: dict[ProviderName, Path] = Field(min_length=1)
    output_format: PipelineOutputFormat = PipelineOutputFormat.JSONL
    export_id: str = "provider-pipeline"
    allow_credential_gated: bool = False
    allow_export_import_only: bool = False

    @model_validator(mode="after")
    def providers_are_unique(self) -> Self:
        if len(self.inputs) != len(set(self.inputs)):
            msg = "provider pipeline inputs must use unique providers"
            raise ValueError(msg)
        return self

    @classmethod
    def from_registry_fixtures(
        cls,
        providers: tuple[ProviderName, ...],
        *,
        registry: ProviderRegistry = DEFAULT_PROVIDER_REGISTRY,
        root: Path = Path(),
        output_format: PipelineOutputFormat = PipelineOutputFormat.JSONL,
    ) -> Self:
        inputs: dict[ProviderName, Path] = {}
        for provider in providers:
            spec = registry.get(provider)
            if not spec.fixtures:
                msg = f"provider {provider.value} has no registered fixtures"
                raise PipelineError(msg)
            inputs[provider] = root / spec.fixtures[0].path
        return cls(inputs=inputs, output_format=output_format)


class ProviderPipelineResult(StrictSchemaModel):
    sources: tuple[ProviderPipelineSource, ...]
    raw_records: tuple[ProviderPipelineRawRecord, ...]
    ingestions: tuple[IngestionResult, ...]
    works: tuple[Work, ...]
    manifest: ExportManifest
    compatibility: CompatibilityProfile

    @model_validator(mode="after")
    def result_counts_match(self) -> Self:
        if self.manifest.record_count != len(self.works):
            msg = "provider pipeline manifest record_count must match works"
            raise ValueError(msg)
        if len(self.sources) != len(self.ingestions) or len(self.raw_records) != len(self.ingestions):
            msg = "provider pipeline source, raw record, and ingestion counts must match"
            raise ValueError(msg)
        return self


def run_provider_pipeline(
    request: ProviderPipelineRequest,
    *,
    registry: ProviderRegistry = DEFAULT_PROVIDER_REGISTRY,
    settings: PyBibXSettings | None = None,
) -> ProviderPipelineResult:
    app_settings = settings or load_settings()
    sources: list[ProviderPipelineSource] = []
    raw_records: list[ProviderPipelineRawRecord] = []
    ingestions: list[IngestionResult] = []
    works: list[Work] = []
    output_format = request.output_format.to_output_format()

    for provider, source_path in request.inputs.items():
        spec = registry.get(provider)
        _validate_access_mode(spec, request)
        _validate_provider_settings(spec, app_settings)
        if not source_path.exists():
            msg = f"provider input does not exist: {source_path}"
            raise PipelineError(msg)
        try:
            ingestion = ingest_provider_file(source_path, provider=provider)
        except IngestionError as exc:
            msg = f"failed to ingest {provider.value}: {exc}"
            raise PipelineError(msg) from exc
        except ValueError as exc:
            msg = f"failed to ingest {provider.value}: {exc}"
            raise PipelineError(msg) from exc
        sources.append(_source(spec, ingestion))
        raw_records.append(_raw_record(spec, ingestion))
        ingestions.append(ingestion)
        works.extend(ingestion.works)

    compatibility = CompatibilityProfile(
        output=VersionStamp(surface=VersionedSurface.OUTPUT, name=output_format.value, version="1.0.0"),
    )
    return ProviderPipelineResult(
        sources=tuple(sources),
        raw_records=tuple(raw_records),
        ingestions=tuple(ingestions),
        works=tuple(works),
        manifest=ExportManifest(
            export_id=request.export_id,
            export_profile=ExportProfile.NORMALIZED_RECORDS
            if output_format is OutputFormat.JSONL
            else ExportProfile.CSL_BIBLIOGRAPHY,
            output_format=output_format,
            record_count=len(works),
            compatibility=compatibility,
        ),
        compatibility=compatibility,
    )


def export_provider_pipeline_result(
    result: ProviderPipelineResult,
    path: Path,
    output_format: PipelineOutputFormat | None = None,
) -> Path:
    selected_format = output_format or PipelineOutputFormat(result.manifest.output_format.value)
    path.parent.mkdir(parents=True, exist_ok=True)
    if selected_format is PipelineOutputFormat.JSONL:
        lines = [work.model_dump_json() for work in result.works]
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        return path
    if selected_format is PipelineOutputFormat.CSL_JSON:
        path.write_text(json.dumps(export_csl_json(result.works), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path
    msg = f"unsupported provider pipeline export format: {selected_format.value}"
    raise PipelineError(msg)


def _validate_access_mode(spec: ProviderSpec, request: ProviderPipelineRequest) -> None:
    if spec.access_mode is ProviderAccessMode.CREDENTIAL_GATED and not request.allow_credential_gated:
        msg = f"{spec.provider.value} is credential-gated and not enabled for the offline provider pipeline"
        raise PipelineError(msg)
    if spec.access_mode is ProviderAccessMode.EXPORT_IMPORT_ONLY and not request.allow_export_import_only:
        msg = f"{spec.provider.value} is export/import-only and not enabled for the open-provider pipeline"
        raise PipelineError(msg)


def _validate_provider_settings(spec: ProviderSpec, settings: PyBibXSettings) -> None:
    provider_settings = settings.provider_settings(spec.provider)
    if provider_settings is None:
        msg = f"{spec.provider.value} is missing from PyBibX settings"
        raise PipelineError(msg)
    if not provider_settings.enabled:
        msg = f"{spec.provider.value} is disabled in PyBibX settings"
        raise PipelineError(msg)


def _source(spec: ProviderSpec, ingestion: IngestionResult) -> ProviderPipelineSource:
    return ProviderPipelineSource(
        provider=spec.provider,
        source_path=ingestion.source_path,
        input_format=ingestion.input_format,
        provider_version=_provider_version(spec),
        input_version=_input_version(ingestion.input_format),
        access_mode=spec.access_mode,
        terms_note=spec.terms_note,
    )


def _raw_record(spec: ProviderSpec, ingestion: IngestionResult) -> ProviderPipelineRawRecord:
    data = ingestion.source_path.read_bytes()
    return ProviderPipelineRawRecord(
        provider=spec.provider,
        source_path=ingestion.source_path,
        input_format=ingestion.input_format,
        content_digest=f"sha256:{hashlib.sha256(data).hexdigest()}",
        byte_count=len(data),
        provider_version=_provider_version(spec),
        input_version=_input_version(ingestion.input_format),
    )


def _provider_version(spec: ProviderSpec) -> VersionStamp:
    return VersionStamp(surface=VersionedSurface.PROVIDER, name=spec.provider.value, version=spec.version.version)


def _input_version(input_format: InputFormat) -> VersionStamp:
    return VersionStamp(surface=VersionedSurface.INPUT, name=input_format.value, version="1.0.0")
