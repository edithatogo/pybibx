# Provider Registry Fixtures Verification

Verified at `2026-06-23T17:32:17Z`.

## Local Evidence

- `uv lock --check`: passed.
- `uv run --group dev pytest tests -q`: passed, `18 passed`.
- `uv run --group dev ruff check pybibx setup.py tests`: passed.
- `uv run --group dev ruff format --check pybibx setup.py tests`: passed.
- `uv run --group dev pyright`: passed with strict mode.
- `uv run --group dev ty check pybibx/__init__.py`: passed.
- `python scripts/check_conductor_swarm.py`: passed.
- `git diff --check`: passed.
- `vale conductor README.md`: passed with 0 errors and 0 warnings; existing docs produce spelling suggestions only.

## Implemented Surface

- Added `pybibx.providers` with access modes, capabilities, endpoints, fixture specs, provider specs, and registry query helpers.
- Registered OpenAlex, Crossref, PubMed, MEDLINE, OpenCitations, Semantic Scholar, ROR, ORCID, Unpaywall, arXiv, bioRxiv, medRxiv, Google Scholar export import, Scopus, and Web of Science.
- Marked Scopus and Web of Science as credential-gated and disabled by default in settings.
- Marked Google Scholar as export/import-only with no live endpoint and a non-scraping terms note.
- Added minimal local fixtures for every registered provider under `tests/fixtures/providers`.
- Extended default settings so every registered provider has a matching settings entry.

## Known Boundaries

- This track does not implement live HTTP clients, provider adapters, Polars ingestion, retries, pagination, or credential loading.
- Provider URLs and terms notes are registry metadata for the next adapter track; each live adapter must verify current provider documentation and terms before use.
- Credential-gated providers remain disabled by default.
