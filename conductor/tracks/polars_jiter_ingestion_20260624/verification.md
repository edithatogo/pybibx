# Polars Jiter Ingestion Verification

Verified at `2026-06-23T17:47:59Z`.

## Local Evidence

- `uv lock`: passed and refreshed direct dependency metadata for baseline `polars` and `jiter`.
- `uv lock --check`: passed.
- `uv run --group dev pytest tests -q`: passed, `36 passed`.
- `uv run --group dev ruff check pybibx setup.py tests`: passed.
- `uv run --group dev ruff format --check pybibx setup.py tests`: passed.
- `uv run --group dev pyright`: passed with strict mode and 0 warnings.
- `uv run --group dev ty check pybibx/__init__.py`: passed.
- `python scripts/check_conductor_swarm.py`: passed.
- `git diff --check`: passed.

## Implemented Surface

- Added `pybibx.ingestion` with `IngestionResult`, `IngestionError`, `load_json_payload`, `scan_tabular`, and `ingest_provider_file`.
- Used Jiter for JSON fixture parsing and Polars lazy `scan_csv` for CSV/tabular export ingestion.
- Normalized provider fixture payloads into schema-layer `Work` records with provider/input compatibility metadata.
- Covered OpenAlex, Crossref, PubMed, MEDLINE, OpenCitations, Semantic Scholar, ROR, ORCID, Unpaywall, arXiv, bioRxiv, medRxiv, Scopus CSV export, Web of Science tabular export, and Google Scholar BibTeX export.
- Promoted `polars` and `jiter` to baseline dependencies because maintained ingestion code imports them directly.

## Known Boundaries

- No live API clients, pagination, retries, bulk downloads, credential loading, or Polars production pipelines were added.
- The ingestion layer consumes local files and fixtures only; provider-specific network adapters are deferred.
- Legacy `pybibx/base` pandas-heavy runtime was not modified.
