"""Regression checks for the packaging and tooling foundation."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXPECTED_PYTHON = ">=3.14,<3.15"
EXPECTED_VERSION = "5.9.2"


def read_toml(path: str) -> dict[str, object]:
    return tomllib.loads((REPO / path).read_text(encoding="utf-8"))


def test_project_metadata_preserves_current_release_identity() -> None:
    pyproject = read_toml("pyproject.toml")
    project = pyproject["project"]

    assert isinstance(project, dict)
    assert project["name"] == "pybibx"
    assert project["version"] == EXPECTED_VERSION
    assert project["requires-python"] == EXPECTED_PYTHON
    assert project["readme"] == "README.md"


def test_dependency_groups_separate_legacy_and_modern_stacks() -> None:
    pyproject = read_toml("pyproject.toml")
    extras = pyproject["project"]["optional-dependencies"]  # type: ignore[index]
    dependency_groups = pyproject["dependency-groups"]

    assert isinstance(extras, dict)
    assert "jiter" in pyproject["project"]["dependencies"]  # type: ignore[index]
    assert "polars" in pyproject["project"]["dependencies"]  # type: ignore[index]
    assert "pydantic>=2" in pyproject["project"]["dependencies"]  # type: ignore[index]
    assert "pydantic-settings" in pyproject["project"]["dependencies"]  # type: ignore[index]
    assert "rustworkx" in pyproject["project"]["dependencies"]  # type: ignore[index]
    assert extras["schema"] == []
    assert extras["data"] == []
    assert "great-expectations" in extras["quality"]
    assert "deepchecks" in extras["quality"]
    assert "kedro" in extras["quality"]
    assert extras["graph"] == []
    assert "loguru" in extras["observability"]
    assert "logfire" in extras["observability"]
    assert "opentelemetry-sdk" in extras["observability"]
    assert "lancedb" in extras["rag"]
    assert extras["reports"] == []
    assert "reflex" in extras["ui"]
    assert "reflex" in extras["modern"]
    assert "scalene" in dependency_groups["dev"]  # type: ignore[index]
    assert "pytest-gremlins" in dependency_groups["dev"]  # type: ignore[index]


def test_quality_tool_configs_are_present_and_scoped() -> None:
    pyproject = read_toml("pyproject.toml")
    pixi = read_toml("pixi.toml")
    pyright = json.loads((REPO / "pyrightconfig.json").read_text(encoding="utf-8"))
    renovate = json.loads((REPO / "renovate.json").read_text(encoding="utf-8"))

    assert pyproject["tool"]["ruff"]["target-version"] == "py314"  # type: ignore[index]
    assert pyproject["tool"]["ty"]["environment"]["python-version"] == "3.14"  # type: ignore[index]
    assert pyproject["tool"]["ty"]["src"]["exclude"] == ["pybibx/base"]  # type: ignore[index]
    assert pyproject["tool"]["ty"]["rules"]["all"] == "error"  # type: ignore[index]
    assert pyproject["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests"]  # type: ignore[index]
    assert pyright["typeCheckingMode"] == "strict"
    assert pyright["include"] == ["pybibx"]
    assert pixi["feature"]["dev"]["tasks"]["swarm-doctor"] == "python scripts/conductor_swarm.py doctor"  # type: ignore[index]
    assert pixi["feature"]["dev"]["tasks"]["mutate"] == "uv run pytest-gremlins tests"  # type: ignore[index]
    assert "scalene --json" in pixi["feature"]["dev"]["tasks"]["profile-ingestion"]  # type: ignore[index]
    assert "pybibx/ingestion/parsers.py" in pixi["feature"]["dev"]["tasks"]["profile-ingestion"]  # type: ignore[index]
    assert "scalene --json" in pixi["feature"]["dev"]["tasks"]["profile-graph"]  # type: ignore[index]
    assert "pybibx/graph/builders.py" in pixi["feature"]["dev"]["tasks"]["profile-graph"]  # type: ignore[index]
    assert "config:recommended" in renovate["extends"]


def test_python314_baseline_sync_does_not_require_all_extras() -> None:
    pixi = read_toml("pixi.toml")
    workflow = (REPO / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
    dependency_policy = (REPO / "conductor" / "dependency-policy.md").read_text(encoding="utf-8")

    assert "run: uv sync --group dev" in workflow
    assert "--all-extras" not in workflow
    assert pixi["feature"]["dev"]["tasks"]["sync"] == "uv sync --group dev"  # type: ignore[index]
    assert pixi["feature"]["dev"]["tasks"]["sync-all-extras"] == "uv sync --all-extras --group dev"  # type: ignore[index]
    assert "not a baseline-safe command on Python 3.14" in dependency_policy
    assert "gensim" in dependency_policy


def test_prose_and_ci_configs_reference_required_tools() -> None:
    vale = (REPO / ".vale.ini").read_text(encoding="utf-8")
    workflow = (REPO / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")

    assert "PyBibX" in vale
    assert "astral-sh/ruff-action@v3" in workflow
    assert "uv run pyright" in workflow
    assert "uv run ty check pybibx/__init__.py" in workflow
