"""Regression tests for quality, observability, and performance lanes."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from pydantic import ValidationError

from pybibx.quality import (
    DataQualityLane,
    KedroNodeSpec,
    ObservabilityBackend,
    ObservabilityPlan,
    build_default_quality_observability_plan,
    build_observability_plan,
    build_pytest_gremlins_spec,
    build_scalene_profile,
    create_kedro_pipeline,
    default_data_quality_suites,
)
from pybibx.schemas import ProviderName
from pybibx.settings import ObservabilitySettings, PyBibXSettings, QualitySettings

EXPECTED_DEFAULT_SUITE_COUNT = 4
EXPECTED_PLAN_SUITE_COUNT = 6
EXPECTED_PROFILE_COUNT = 2


def test_quality_package_imports_without_optional_quality_dependencies() -> None:
    module = importlib.import_module("pybibx.quality")

    assert module.DataQualityLane.GREAT_EXPECTATIONS.value == "great-expectations"


def test_default_data_quality_suites_cover_great_expectations_and_deepchecks() -> None:
    suites = default_data_quality_suites((ProviderName.OPENALEX, ProviderName.CROSSREF))

    assert len(suites) == EXPECTED_DEFAULT_SUITE_COUNT
    assert {suite.lane for suite in suites} == {DataQualityLane.GREAT_EXPECTATIONS, DataQualityLane.DEEPCHECKS}
    assert all(suite.fail_on_warning for suite in suites)
    assert all("work_id" in suite.required_columns for suite in suites)


def test_kedro_pipeline_validates_unique_nodes_and_node_output_dependencies() -> None:
    pipeline = create_kedro_pipeline()

    assert pipeline.lane is DataQualityLane.KEDRO
    assert [node.name for node in pipeline.nodes] == [
        "load-provider-fixture",
        "normalize-work-records",
        "validate-normalized-records",
    ]

    with pytest.raises(ValidationError, match="unique"):
        create_kedro_pipeline(
            (
                KedroNodeSpec(name="same", outputs=("node:a",)),
                KedroNodeSpec(name="same", outputs=("node:b",)),
            ),
        )

    with pytest.raises(ValidationError, match="missing node outputs"):
        create_kedro_pipeline((KedroNodeSpec(name="bad", inputs=("node:missing",), outputs=("node:out",)),))


def test_observability_plan_respects_loguru_logfire_otel_and_prometheus_settings() -> None:
    settings = PyBibXSettings(
        observability=ObservabilitySettings(
            log_level="DEBUG",
            logfire_enabled=True,
            opentelemetry_enabled=True,
            otlp_endpoint="http://localhost:4318",
            prometheus_enabled=True,
        ),
    )
    plan = build_observability_plan(settings)

    assert plan.backends == (
        ObservabilityBackend.LOGURU,
        ObservabilityBackend.LOGFIRE,
        ObservabilityBackend.OPENTELEMETRY,
        ObservabilityBackend.PROMETHEUS,
    )
    assert plan.log_level == "DEBUG"
    assert plan.otlp_endpoint == "http://localhost:4318"

    with pytest.raises(ValidationError, match="OpenTelemetry"):
        ObservabilityPlan(backends=(ObservabilityBackend.LOGURU,), log_level="INFO", otlp_endpoint="http://otel")


def test_scalene_and_pytest_gremlins_specs_generate_reviewable_commands() -> None:
    profile = build_scalene_profile("pybibx/ingestion/parsers.py", output_dir=Path(".profiles"))
    gremlins = build_pytest_gremlins_spec("tests/test_polars_jiter_ingestion.py", seed=42)

    assert profile.tool == "scalene"
    assert profile.command == (
        "scalene",
        "--json",
        "--outfile",
        ".profiles/parsers.scalene.json",
        "pybibx/ingestion/parsers.py",
    )
    assert gremlins.tool == "pytest-gremlins"
    assert gremlins.command == ("pytest-gremlins", "--seed", "42", "tests/test_polars_jiter_ingestion.py")


def test_default_quality_observability_plan_combines_all_requested_lanes() -> None:
    settings = PyBibXSettings(quality=QualitySettings(profile_output_path=Path(".profiles")))
    plan = build_default_quality_observability_plan(settings)

    assert len(plan.data_quality_suites) == EXPECTED_PLAN_SUITE_COUNT
    assert plan.kedro_pipeline.pipeline_name == "pybibx-quality-ingestion"
    assert plan.observability.backends == (ObservabilityBackend.LOGURU,)
    assert len(plan.scalene_profiles) == EXPECTED_PROFILE_COUNT
    assert plan.gremlins.target == "tests"
