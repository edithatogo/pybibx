# End-To-End Provider Pipeline Verification

Verified at `2026-06-25T08:11:48Z`.

## Local Evidence

- `uv lock --check`: passed.
- `uv run --group dev pytest tests/test_provider_pipeline.py -q`: passed, `7 passed`.
- `uv run --group dev pytest tests -q`: passed, `99 passed`.
- `uv run --group dev ruff check pybibx setup.py tests`: passed.
- `uv run --group dev ruff format --check pybibx setup.py tests`: passed.
- `uv run --group dev pyright`: passed.
- `uv run --group dev pyright pybibx/pipeline tests/test_provider_pipeline.py`: passed.
- `uv run --group dev ty check pybibx/__init__.py pybibx/pipeline`: passed.
- `python scripts/check_conductor_swarm.py`: passed.
- `python scripts/conductor_swarm.py validate-config --json`: passed.
- `python scripts/conductor_swarm.py plan --json`: passed and reports Codex swarm fallback active while Cline remains non-TTY blocked.

## Implemented Surface

- Added `pybibx.pipeline` with immutable request/result models for offline provider pipeline execution.
- Added provider pipeline source and raw-record audit metadata with SHA-256 digests, byte counts, provider versions, input versions, access modes, and provider terms notes.
- Added `run_provider_pipeline` to compose provider registry lookup, settings, Polars/Jiter ingestion, Pydantic records, output compatibility metadata, and export manifests.
- Added deterministic JSONL and CSL-JSON export support through `export_provider_pipeline_result`.
- Added `python -m pybibx.pipeline` and `pybibx-provider-pipeline` for offline fixture-driven CLI execution.
- Added tests for OpenAlex, Crossref, PubMed, and MEDLINE fixture ingestion, registry fixture selection, JSONL/CSL export output, invalid provider names, disabled settings, credential-gated/export-only access boundaries, missing input files, schema failure wrapping, and CLI execution.

## Known Boundaries

- No live provider network clients or credentialed provider downloads were added.
- Scopus and Web of Science remain credential-gated; Google Scholar remains export/import-only and is rejected by the open-provider pipeline unless explicitly allowed.
- Baseline validation intentionally used `uv sync --group dev` behavior through `uv run --group dev`; all-extras remains non-baseline on Python 3.14.
- Cline/DeepSeek remains blocked in this non-TTY Codex session because `cline config --json` requires an interactive TTY; Codex handled implementation and review locally.
