# Release Readiness Specification

## Overview

Prepare the PyBibX 6.0 alpha boundary after the maintained foundations and first productized pipeline are in place. This track should make the repository understandable, installable, auditable, and safe for early adopters without claiming that every optional future integration is complete.

## Functional Requirements

- Define the PyBibX 6.0 alpha public API surface and mark unstable/internal modules.
- Add or refresh migration notes from 5.9.2 to the maintained 6.0 modules.
- Add an optional-extra compatibility matrix that separates baseline, legacy, quality, AI, RAG, UI/reporting, and all-extras paths.
- Add release notes that summarize completed Conductor tracks, known limitations, and external blockers.
- Add package/build checks for wheel metadata, import smoke, and README/package long-description health.
- Add documentation examples for schema/settings, provider pipeline, legacy bridge, reports, and quality lanes as available.
- Confirm Renovate, Ruff Action, Pyright, ty, pytest, Vale, and GitHub Actions quality gates are documented and current.

## Non-Functional Requirements

- Must not promote optional all-extras to baseline until the legacy NLP dependency stack is Python 3.14-safe.
- Must not claim Cline/DeepSeek, paid providers, hosted LLMs, Reflex, Cosmograph, Rig, Graphina, PyG, PDFMux, or Monty are production-ready unless verified.
- Must preserve PyBibX 5.9.2 compatibility boundaries and explicitly label the 6.0 alpha as maintained/refactor-line work.
- Must keep docs concise, source-aware, and aligned with existing Conductor product/requirements/design docs.

## Acceptance Criteria

- Release-readiness docs identify public, provisional, optional, and legacy compatibility surfaces.
- Package build and import smoke checks pass locally.
- The optional-extra compatibility matrix explains baseline-safe and non-baseline install paths.
- GitHub Actions quality passes on the pushed release-readiness commit.
- Conductor verification records remaining external/manual gates separately from repo-local completion.

## Out Of Scope

- Publishing to PyPI.
- Tagging a release without explicit user instruction.
- Resolving every optional dependency or external provider credential.
- Rewriting large docs beyond the release-readiness boundary.
