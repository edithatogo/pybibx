# Polars Jiter Ingestion Verification

Verified at `2026-06-24T03:20:11Z`.

## Implemented Surface

- Added `pybibx.ingestion` with `IngestionResult`, `IngestionError`, `load_json_payload`, `scan_jsonl`, `scan_tabular`, and `ingest_provider_file`.
- Used Jiter for JSON fixture parsing.
- Used Polars lazy `scan_ndjson` for JSONL paths and Polars lazy `scan_csv` for CSV/TSV tabular export ingestion.
- Normalized provider fixture payloads into schema-layer `Work` records with provider/input/schema/library/settings compatibility metadata.
- Covered OpenAlex, Crossref, PubMed, MEDLINE, OpenCitations, Semantic Scholar, ROR, ORCID, Unpaywall, arXiv, bioRxiv, medRxiv, Scopus CSV/RIS exports, Web of Science TSV exports, and Google Scholar BibTeX exports.
- Added fail-closed inference for unsupported provider/format combinations and unrecognized `.txt` files.
- Preserved the legacy `pybibx/base` pandas-heavy runtime untouched.

## Manual Checkpoints

- Phase 1 expected files and settings exist: `pybibx/ingestion/__init__.py`, `pybibx/ingestion/parsers.py`, ingestion result/error types, Jiter JSON loader, Polars JSONL/tabular lazy scan helpers, and local file format inference for JSON, JSONL, CSV, TSV, BibTeX, and RIS.
- Phase 1 acceptance criteria are met: ingestion lives outside `pybibx/base`, JSON uses Jiter, JSONL/CSV/TSV use Polars lazy readers, and unsupported local formats fail closed.
- Phase 2 expected normalization paths exist for JSON providers, Scopus tabular/RIS exports, Web of Science TSV exports, and Google Scholar BibTeX exports.
- Phase 2 acceptance criteria are met: normalized `Work` records preserve provider, input, schema, library, and settings metadata.
- Phase 3 expected tests exist in `tests/test_polars_jiter_ingestion.py` and provider registry compatibility remains covered by `tests/test_provider_registry.py`.
- Phase 3 acceptance criteria are met locally. The only remaining step is the archive commit after this verification commit passes GitHub Actions.
- No unrelated implementation files were modified for this closeout.

## Local Evidence

- `uv run --group dev pytest tests/test_polars_jiter_ingestion.py -q`: passed, `26 passed`.
- `uv run --group dev pytest tests/test_provider_registry.py tests/test_polars_jiter_ingestion.py -q`: passed, `34 passed`.
- `uv lock --check`: passed.
- `uv run --group dev pytest tests -q`: passed, `79 passed`.
- `uv run --group dev ruff check pybibx/ingestion tests/test_polars_jiter_ingestion.py`: passed.
- `uv run --group dev ruff check pybibx setup.py tests`: passed.
- `uv run --group dev ruff format --check pybibx setup.py tests`: passed after formatting `tests/test_polars_jiter_ingestion.py`.
- `uv run --group dev pyright pybibx/ingestion tests/test_polars_jiter_ingestion.py`: passed with 0 errors, 0 warnings, and 0 informations.
- `uv run --group dev pyright`: passed with 0 errors, 0 warnings, and 0 informations.
- `uv run --group dev ty check pybibx/__init__.py`: passed.
- `python scripts/check_conductor_swarm.py`: passed.
- `python scripts/conductor_swarm.py validate-config --json`: passed.
- `python scripts/conductor_swarm.py plan --json`: passed and preserved the Codex fallback lane while Cline remains non-TTY blocked.
- `git diff --check`: passed.
- `vale conductor README.md`: passed with 0 errors and 0 warnings; existing docs produce spelling suggestions only.
- Verification commit `e00a380acecdddc542ef774e782bc6d69a335c2e` passed GitHub Actions `quality` run `28072874295`.

## Review Evidence

- Deputy reviewer found closeout blockers that were fixed or queued for archive: stale verification evidence, missing review evidence, thin manual checkpoints, missing CI evidence, and active registry state.
- Implementation-coverage reviewer found no blocking defects and recommended stronger tests for Jiter proof, compatibility metadata, and fail-closed cases; those tests were added.
- Parser-contract reviewer found three blockers that were fixed: advertised RIS without parser support, BibTeX multi-entry truncation, and provider-blind `.txt` inference.

## Known Boundaries

- No live API clients, pagination, retries, bulk downloads, credential loading, or Polars production pipelines were added.
- The ingestion layer consumes local files and fixtures only; provider-specific network adapters are deferred.
- Legacy `pybibx/base` pandas-heavy runtime was not modified.
