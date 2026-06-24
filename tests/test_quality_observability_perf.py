"""Regression tests for quality, observability, and performance lanes."""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
from pydantic import ValidationError

from pybibx.providers import DEFAULT_PROVIDER_REGISTRY
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
EXPECTED_PROFILE_COUNT = 2


def test_quality_package_imports_without_optional_quality_dependencies() -> None:
    code = textwrap.dedent(
        """
        import sys
        from importlib.abc import MetaPathFinder

        blocked = {
            'great_expectations', 'deepchecks', 'kedro', 'loguru', 'logfire',
            'opentelemetry', 'prometheus_client', 'scalene', 'pytest_gremlins',
            'pandas', 'numpy', 'scipy', 'sklearn', 'torch', 'transformers',
            'gensim', 'flask', 'pybibx.base', 'pybibx.base.pbx',
        }

        class Blocker(MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                if any(fullname == item or fullname.startswith(f'{item}.') for item in blocked):
                    raise AssertionError(fullname)
                return None

        sys.meta_path.insert(0, Blocker())
        import pybibx.quality as quality

        assert quality.DataQualityLane.GREAT_EXPECTATIONS.value == 'great-expectations'
        loaded = blocked.intersection(sys.modules)
        assert not loaded, sorted(loaded)
        """,
    )

    subprocess.run([sys.executable, "-c", code], check=True)  # noqa: S603


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

    with pytest.raises(ValidationError, match="outputs must be unique"):
        create_kedro_pipeline(
            (
                KedroNodeSpec(name="first", outputs=("node:shared",)),
                KedroNodeSpec(name="second", outputs=("node:shared",)),
            ),
        )

    with pytest.raises(ValidationError, match="cannot consume its own outputs"):
        create_kedro_pipeline((KedroNodeSpec(name="cycle", inputs=("node:self",), outputs=("node:self",)),))


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
    fixture_providers = tuple(spec.provider for spec in DEFAULT_PROVIDER_REGISTRY.specs if spec.fixtures)

    assert len(plan.data_quality_suites) == len(fixture_providers) * 2
    assert {suite.provider for suite in plan.data_quality_suites} == set(fixture_providers)
    assert plan.kedro_pipeline is not None
    assert plan.kedro_pipeline.pipeline_name == "pybibx-quality-ingestion"
    assert plan.observability.backends == (ObservabilityBackend.LOGURU,)
    assert len(plan.scalene_profiles) == EXPECTED_PROFILE_COUNT
    assert {profile.target for profile in plan.scalene_profiles} == {
        "pybibx/ingestion/parsers.py",
        "pybibx/graph/builders.py",
    }
    assert plan.gremlins is not None
    assert plan.gremlins.target == "tests"


def test_default_quality_observability_plan_honors_quality_lane_flags() -> None:
    plan = build_default_quality_observability_plan(
        PyBibXSettings(
            quality=QualitySettings(
                great_expectations_enabled=False,
                deepchecks_enabled=False,
                kedro_enabled=False,
                scalene_enabled=False,
                pytest_gremlins_enabled=False,
            ),
        ),
    )

    assert plan.data_quality_suites == ()
    assert plan.kedro_pipeline is None
    assert plan.scalene_profiles == ()
    assert plan.gremlins is None
