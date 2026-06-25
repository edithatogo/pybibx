"""Release-readiness contract checks."""

from __future__ import annotations

import importlib
import tomllib
from pathlib import Path

from pybibx.release import (
    EXTRA_COMPATIBILITY,
    LOCAL_QUALITY_GATES,
    RELEASE_SURFACE,
    ExtraCompatibilityKind,
    ReleaseSurfaceKind,
    release_readiness_contract,
)

REPO = Path(__file__).resolve().parents[1]
REQUIRED_DOCS = (
    REPO / "docs" / "release-readiness.md",
    REPO / "docs" / "migration-5.9.2-to-6-alpha.md",
)


def test_release_contract_classifies_public_and_blocked_surfaces() -> None:
    contract = release_readiness_contract()
    surfaces = {item.module: item for item in contract.surfaces}
    extras = {item.extra: item for item in contract.extras}

    assert surfaces["pybibx.schemas"].kind is ReleaseSurfaceKind.PUBLIC
    assert surfaces["pybibx.release"].kind is ReleaseSurfaceKind.PUBLIC
    assert surfaces["pybibx.legacy"].kind is ReleaseSurfaceKind.PUBLIC
    assert surfaces["pybibx.base"].kind is ReleaseSurfaceKind.LEGACY
    assert surfaces["pybibx.base.*"].kind is ReleaseSurfaceKind.INTERNAL
    assert surfaces["pybibx.rag"].kind is ReleaseSurfaceKind.OPTIONAL
    assert extras["baseline"].baseline is True
    assert extras["baseline"].kind is ExtraCompatibilityKind.BASELINE_SAFE
    assert extras["licensed-providers"].kind is ExtraCompatibilityKind.CREDENTIAL_GATED
    assert extras["all"].kind is ExtraCompatibilityKind.BLOCKED
    assert "--all-extras" in extras["all"].install_command
    assert any("PyPI" in gate for gate in contract.external_gates)


def test_release_surface_exports_match_runtime_all_exports() -> None:
    for surface in RELEASE_SURFACE:
        if not surface.exports or surface.module == "pybibx.base":
            continue
        module = importlib.import_module(surface.module)
        module_exports = set(getattr(module, "__all__", ()))
        assert set(surface.exports) <= module_exports, surface.module


def test_optional_extra_matrix_matches_pyproject_and_dependency_policy() -> None:
    pyproject = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    extras = pyproject["project"]["optional-dependencies"]  # type: ignore[index]
    workflow = (REPO / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
    dependency_policy = (REPO / "conductor" / "dependency-policy.md").read_text(encoding="utf-8")
    release_extras = {item.extra: item for item in EXTRA_COMPATIBILITY}

    assert "run: uv sync --group dev" in workflow
    assert "--all-extras" not in workflow
    assert "not a baseline-safe command on Python 3.14" in dependency_policy
    assert "all" in extras
    assert release_extras["all"].kind is ExtraCompatibilityKind.BLOCKED
    assert release_extras["legacy"].kind is ExtraCompatibilityKind.PROBING_ONLY


def test_release_docs_and_readme_are_present_and_alpha_bounded() -> None:
    readme = (REPO / "README.md").read_text(encoding="utf-8")

    assert "# PyBibX 6.0 Alpha Release Readiness" in REQUIRED_DOCS[0].read_text(encoding="utf-8")
    assert "Migration Notes: PyBibX 5.9.2 To 6.0 Alpha" in REQUIRED_DOCS[1].read_text(encoding="utf-8")
    assert "pip install pybibx" in readme
    for doc in REQUIRED_DOCS:
        text = doc.read_text(encoding="utf-8")
        assert "all-extras" in text
        assert "production-ready" in text or "planning contracts" in text
        assert "PyPI" in text


def test_quality_gate_documentation_mentions_current_tools() -> None:
    release_doc = REQUIRED_DOCS[0].read_text(encoding="utf-8")
    workflow = (REPO / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
    renovate = (REPO / "renovate.json").read_text(encoding="utf-8")

    assert "astral-sh/ruff-action@v3" in workflow
    assert "config:recommended" in renovate
    for gate in LOCAL_QUALITY_GATES:
        assert gate in release_doc
