from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Self

from pydantic import Field, model_validator

from pybibx.providers import DEFAULT_PROVIDER_REGISTRY, ProviderCapability
from pybibx.schemas import ProviderName  # noqa: TC001 - Pydantic resolves this model at runtime.
from pybibx.schemas.records import StrictSchemaModel
from pybibx.settings import PyBibXSettings

if TYPE_CHECKING:
    from collections.abc import Sequence


class DataQualityLane(StrEnum):
    GREAT_EXPECTATIONS = "great-expectations"
    DEEPCHECKS = "deepchecks"
    KEDRO = "kedro"


class ObservabilityBackend(StrEnum):
    LOGURU = "loguru"
    LOGFIRE = "logfire"
    OPENTELEMETRY = "opentelemetry"
    PROMETHEUS = "prometheus"


class DataQualitySuiteSpec(StrictSchemaModel):
    lane: DataQualityLane
    suite_name: str = Field(min_length=1)
    provider: ProviderName | None = None
    required_columns: tuple[str, ...] = Field(default_factory=tuple)
    expectation_count: int = Field(default=0, ge=0)
    fail_on_warning: bool = True


class GreatExpectationsSuiteSpec(DataQualitySuiteSpec):
    lane: DataQualityLane = DataQualityLane.GREAT_EXPECTATIONS
    checkpoint_name: str = Field(min_length=1)
    datasource_name: str = "pybibx-polars-fixtures"


class DeepchecksSuiteSpec(DataQualitySuiteSpec):
    lane: DataQualityLane = DataQualityLane.DEEPCHECKS
    check_suite_name: str = Field(min_length=1)
    drift_reference_required: bool = False


class KedroNodeSpec(StrictSchemaModel):
    name: str = Field(min_length=1)
    inputs: tuple[str, ...] = Field(default_factory=tuple)
    outputs: tuple[str, ...] = Field(min_length=1)
    tags: tuple[str, ...] = Field(default_factory=tuple)


class KedroPipelineSpec(StrictSchemaModel):
    lane: DataQualityLane = DataQualityLane.KEDRO
    pipeline_name: str = Field(min_length=1)
    nodes: tuple[KedroNodeSpec, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def node_names_are_unique_and_dependencies_exist(self) -> Self:
        names = [node.name for node in self.nodes]
        if len(names) != len(set(names)):
            msg = "Kedro pipeline node names must be unique"
            raise ValueError(msg)
        produced_output_list = [output for node in self.nodes for output in node.outputs]
        if len(produced_output_list) != len(set(produced_output_list)):
            msg = "Kedro pipeline node outputs must be unique"
            raise ValueError(msg)
        for node in self.nodes:
            if set(node.inputs) & set(node.outputs):
                msg = f"Kedro pipeline node cannot consume its own outputs: {node.name}"
                raise ValueError(msg)
        produced_outputs = set(produced_output_list)
        missing_inputs = sorted(
            input_name
            for node in self.nodes
            for input_name in node.inputs
            if input_name.startswith("node:") and input_name not in produced_outputs
        )
        if missing_inputs:
            msg = f"Kedro pipeline references missing node outputs: {missing_inputs}"
            raise ValueError(msg)
        return self


class ObservabilityPlan(StrictSchemaModel):
    backends: tuple[ObservabilityBackend, ...]
    log_level: str = Field(min_length=1)
    service_name: str = "pybibx"
    otlp_endpoint: str | None = None
    include_validation_events: bool = True
    include_agent_events: bool = True

    @model_validator(mode="after")
    def otel_endpoint_requires_otel(self) -> Self:
        if self.otlp_endpoint is not None and ObservabilityBackend.OPENTELEMETRY not in self.backends:
            msg = "otlp_endpoint requires the OpenTelemetry backend"
            raise ValueError(msg)
        return self


class PerformanceProfileSpec(StrictSchemaModel):
    tool: str = "scalene"
    target: str = Field(min_length=1)
    output_path: Path
    cpu: bool = True
    memory: bool = True
    command: tuple[str, ...]


class MutationRunSpec(StrictSchemaModel):
    tool: str = "pytest-gremlins"
    target: str = Field(min_length=1)
    seed: int = Field(default=0, ge=0)
    command: tuple[str, ...]
    fail_under_survival_rate: float = Field(default=0.0, ge=0.0, le=1.0)


class QualityObservabilityPlan(StrictSchemaModel):
    data_quality_suites: tuple[DataQualitySuiteSpec, ...]
    kedro_pipeline: KedroPipelineSpec | None = None
    observability: ObservabilityPlan
    scalene_profiles: tuple[PerformanceProfileSpec, ...]
    gremlins: MutationRunSpec | None = None


def default_data_quality_suites(
    providers: Sequence[ProviderName],
    *,
    include_great_expectations: bool = True,
    include_deepchecks: bool = True,
) -> tuple[DataQualitySuiteSpec, ...]:
    suites: list[DataQualitySuiteSpec] = []
    for provider in providers:
        if include_great_expectations:
            suites.append(
                GreatExpectationsSuiteSpec(
                    suite_name=f"{provider.value}-normalized-records",
                    checkpoint_name=f"{provider.value}-checkpoint",
                    provider=provider,
                    required_columns=("work_id", "title", "source_provider"),
                    expectation_count=3,
                ),
            )
        if include_deepchecks:
            suites.append(
                DeepchecksSuiteSpec(
                    suite_name=f"{provider.value}-data-quality",
                    check_suite_name=f"{provider.value}-deepchecks",
                    provider=provider,
                    required_columns=("work_id", "title"),
                    expectation_count=2,
                ),
            )
    return tuple(suites)


def create_kedro_pipeline(nodes: Sequence[KedroNodeSpec] | None = None) -> KedroPipelineSpec:
    pipeline_nodes = tuple(nodes) if nodes is not None else _default_kedro_nodes()
    return KedroPipelineSpec(pipeline_name="pybibx-quality-ingestion", nodes=pipeline_nodes)


def build_observability_plan(settings: PyBibXSettings) -> ObservabilityPlan:
    configured = settings.observability
    backends: list[ObservabilityBackend] = []
    if configured.loguru_enabled:
        backends.append(ObservabilityBackend.LOGURU)
    if configured.logfire_enabled:
        backends.append(ObservabilityBackend.LOGFIRE)
    if configured.opentelemetry_enabled:
        backends.append(ObservabilityBackend.OPENTELEMETRY)
    if configured.prometheus_enabled:
        backends.append(ObservabilityBackend.PROMETHEUS)
    return ObservabilityPlan(
        backends=tuple(backends),
        log_level=configured.log_level,
        otlp_endpoint=configured.otlp_endpoint,
    )


def build_scalene_profile(target: str, *, output_dir: Path = Path(".pybibx/profiles")) -> PerformanceProfileSpec:
    output_path = output_dir / f"{Path(target).stem}.scalene.json"
    return PerformanceProfileSpec(
        target=target,
        output_path=output_path,
        command=("scalene", "--json", "--outfile", str(output_path), target),
    )


def build_pytest_gremlins_spec(target: str = "tests", *, seed: int = 0) -> MutationRunSpec:
    return MutationRunSpec(
        target=target,
        seed=seed,
        command=("pytest-gremlins", "--seed", str(seed), target),
    )


def build_default_quality_observability_plan(settings: PyBibXSettings | None = None) -> QualityObservabilityPlan:
    app_settings = settings or PyBibXSettings()
    quality = app_settings.quality
    providers = tuple(spec.provider for spec in DEFAULT_PROVIDER_REGISTRY.specs if spec.fixtures)
    return QualityObservabilityPlan(
        data_quality_suites=default_data_quality_suites(
            providers,
            include_great_expectations=quality.great_expectations_enabled,
            include_deepchecks=quality.deepchecks_enabled,
        ),
        kedro_pipeline=create_kedro_pipeline() if quality.kedro_enabled else None,
        observability=build_observability_plan(app_settings),
        scalene_profiles=(
            (
                build_scalene_profile("pybibx/ingestion/parsers.py", output_dir=quality.profile_output_path),
                build_scalene_profile("pybibx/graph/builders.py", output_dir=quality.profile_output_path),
            )
            if quality.scalene_enabled
            else ()
        ),
        gremlins=build_pytest_gremlins_spec() if quality.pytest_gremlins_enabled else None,
    )


def _default_kedro_nodes() -> tuple[KedroNodeSpec, ...]:
    return (
        KedroNodeSpec(
            name="load-provider-fixture",
            inputs=("provider_fixture",),
            outputs=("node:raw-provider-payload",),
            tags=(ProviderCapability.METADATA_LOOKUP.value,),
        ),
        KedroNodeSpec(
            name="normalize-work-records",
            inputs=("node:raw-provider-payload",),
            outputs=("node:normalized-work-records",),
            tags=("pydantic", "polars"),
        ),
        KedroNodeSpec(
            name="validate-normalized-records",
            inputs=("node:normalized-work-records",),
            outputs=("node:quality-report",),
            tags=(DataQualityLane.GREAT_EXPECTATIONS.value, DataQualityLane.DEEPCHECKS.value),
        ),
    )
