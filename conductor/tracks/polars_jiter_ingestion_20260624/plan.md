# Polars Jiter Ingestion Plan

## Phase 1: Ingestion Contracts

- [x] Task: Add ingestion package.
    - [x] Define ingestion result and error types.
    - [x] Define file-loading helpers for JSON, JSONL, CSV, TSV, and BibTeX exports.
    - [x] Keep implementation outside `pybibx/base`.
- [x] Task: Conductor - User Manual Verification 'Ingestion Contracts' (Protocol in workflow.md)

## Phase 2: Normalization

- [x] Task: Add provider normalization.
    - [x] Normalize JSON provider fixtures into `Work` records.
    - [x] Normalize Scopus/Web of Science tabular exports into `Work` records.
    - [x] Normalize Google Scholar BibTeX exports into `Work` records.
    - [x] Attach provider/input/schema/library version metadata.
- [x] Task: Conductor - User Manual Verification 'Normalization' (Protocol in workflow.md)

## Phase 3: Verification

- [x] Task: Add tests.
    - [x] Cover Jiter JSON parsing.
    - [x] Cover Polars lazy CSV/tabular parsing.
    - [x] Cover normalized metadata and fail-closed unsupported combinations.
- [x] Task: Run quality gates.
    - [x] Run `uv lock --check`.
    - [x] Run Ruff check and format check.
    - [x] Run Pyright, ty, and pytest.
    - [x] Run Conductor swarm smoke.
- [x] Task: Complete and push.
    - [x] Record verification evidence.
    - [x] Mark track complete.
    - [x] Commit and push to `origin main`.
- [x] Task: Conductor - User Manual Verification 'Verification' (Protocol in workflow.md)
