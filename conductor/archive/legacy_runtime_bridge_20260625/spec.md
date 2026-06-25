# Legacy Runtime Bridge Specification

## Overview

Connect the maintained PyBibX 6.0 contracts to the existing PyBibX 5.9.2 runtime without breaking legacy `pbx_probe`, notebook, or web-app workflows. This track should provide compatibility adapters and migration boundaries rather than rewriting the legacy analysis engine.

## Functional Requirements

- Add adapters that convert validated PyBibX 6.0 normalized records into the legacy dataframe shapes required by existing `pybibx/base` analysis paths.
- Add adapters that convert common legacy import outputs into maintained `Work`, `Author`, `Institution`, `Citation`, and export models.
- Preserve legacy import behavior for `pybibx`, `pybibx.web_app`, and `pybibx.web_stop`.
- Document which legacy analyses can be fed from normalized records and which remain unsupported.
- Add migration examples for using the maintained provider pipeline before invoking legacy analyses.
- Keep new bridge code outside `pybibx/base` unless a tiny compatibility hook is unavoidable and covered by tests.

## Non-Functional Requirements

- Must not remove, rename, or change public legacy methods without a migration path.
- Must not make Polars, Pydantic, or optional 6.0 components break legacy imports.
- Must avoid broad pandas refactors in this track; pandas is allowed only as a bridge output/input type for legacy compatibility.
- Must keep all bridge behavior deterministic and tested with small fixtures.

## Acceptance Criteria

- Legacy import smoke tests still pass.
- Normalized `Work` fixtures can be converted into the legacy dataframe shape needed by at least one existing analysis workflow.
- A representative legacy dataframe/export can be converted into maintained schema records.
- Unsupported legacy paths fail with clear typed errors or documented limitations.
- Migration documentation shows the intended 6.0-to-legacy bridge workflow.

## Out Of Scope

- Rewriting the legacy `pbx_probe` implementation.
- Replacing Flask or the legacy web app.
- Live provider clients, full-text RAG, and GPU graph UI.
