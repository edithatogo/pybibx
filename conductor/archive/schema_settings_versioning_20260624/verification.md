# Schema Settings Versioning Verification

Verified at `2026-06-23T17:18:17Z`.

## Local Evidence

- `uv lock`: passed and refreshed direct dependency metadata for baseline Pydantic dependencies.
- `uv lock --check`: passed.
- `uv run --group dev pytest tests -q`: passed, `11 passed`.
- `uv run --group dev ruff check pybibx setup.py tests`: passed.
- `uv run --group dev ruff format --check pybibx setup.py tests`: passed.
- `uv run --group dev pyright`: passed with strict mode.
- `uv run --group dev ty check pybibx/__init__.py`: passed.
- `python scripts/check_conductor_swarm.py`: passed.
- `git diff --check`: passed.
- `vale conductor README.md`: passed with 0 errors and 0 warnings; existing docs produce spelling suggestions only.
- GitHub Actions `quality` passed for archived `main` commit `a134029`: https://github.com/edithatogo/pybibx/actions/runs/28071057799

## Implemented Surface

- Added `pybibx.versioning` with immutable version stamps and compatibility profiles for library, schema, provider, input, output, ontology, and settings metadata.
- Added `pybibx.schemas` with provider/format/ontology enums plus models for authors, institutions, works, citations, ontology facets, evidence sets, and export manifests.
- Added `pybibx.settings` with `pydantic-settings` models for providers, runtime endpoints, storage paths, observability, and feature gates.
- Promoted `pydantic>=2` and `pydantic-settings` to baseline dependencies because maintained modules import them directly.
- Added schema/settings tests for valid records, invalid identifiers, evidence consistency, export constraints, JSON Schema snapshots, version profiles, and environment overrides.

## Known Boundaries

- No provider network clients, Polars ingestion, RustWorkX graph builders, RAG, or AI agents were implemented in this track.
- `uv lock` initially hit intermittent PyPI metadata timeouts while resolving the existing optional all-extras graph; rerun succeeded after metadata warmed.
- Cline DeepSeek swarm launch remains blocked in this non-TTY session by the existing `cline config --json` TTY requirement.

## Review Addendum

Reviewed at `2026-06-24T04:24:41Z`.

- Fixed a strict Pyright-only test typing gap by passing `SecretStr` to `ProviderSettings.api_key` in `tests/test_schema_settings_versioning.py`.
- Re-ran focused schema/settings checks:
  - `uv run --group dev pytest tests/test_schema_settings_versioning.py -q`: passed, `7 passed`.
  - `uv run --group dev ruff check pybibx/schemas pybibx/settings.py pybibx/versioning.py tests/test_schema_settings_versioning.py`: passed.
  - `uv run --group dev ruff format --check pybibx/schemas pybibx/settings.py pybibx/versioning.py tests/test_schema_settings_versioning.py`: passed.
  - `uv run --group dev pyright pybibx/schemas pybibx/settings.py pybibx/versioning.py tests/test_schema_settings_versioning.py`: passed.
- Re-ran baseline-safe project checks:
  - `uv run --group dev pytest tests -q`: passed, `92 passed`.
  - `uv run --group dev ruff check pybibx setup.py tests`: passed.
  - `uv run --group dev pyright`: passed.
  - `uv run --group dev ty check pybibx/__init__.py`: passed.
