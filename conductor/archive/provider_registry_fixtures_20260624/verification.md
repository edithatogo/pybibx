# Provider Registry Fixtures Verification

Verified at `2026-06-24T03:07:46Z`.

## Implemented Surface

- Added `pybibx.providers` with access modes, capabilities, provider-native endpoint response formats, fixture specs, provider specs, and registry query helpers.
- Registered OpenAlex, Crossref, PubMed, MEDLINE, OpenCitations, Semantic Scholar, ROR, ORCID, Unpaywall, arXiv, bioRxiv, medRxiv, Google Scholar export import, Scopus, and Web of Science exactly once.
- Marked Scopus and Web of Science as credential-gated and disabled by default in settings.
- Marked Google Scholar as export/import-only with no live endpoint and a non-scraping terms note.
- Added minimal local fixtures for every registered provider under `tests/fixtures/providers`.
- Added TSV as an explicit input format for tab-delimited exports such as Web of Science.
- Extended default settings so every registered provider has a matching settings entry, matching credential flags, and matching rate limits.
- Updated OpenCitations registry metadata to the current `https://api.opencitations.net/index/v2` surface.

## Manual Checkpoints

- Phase 1 expected files and settings exist: `pybibx/providers/__init__.py`, `pybibx/providers/registry.py`, provider enums, provider endpoint/fixture/spec models, registry query helpers, and default registry entries.
- Phase 1 acceptance criteria are met: every requested provider is registered once, Scopus and Web of Science are the only credential-gated providers, and Google Scholar has no live endpoint.
- Phase 2 expected files and settings exist: provider fixtures under `tests/fixtures/providers`, default provider settings in `pybibx/settings.py`, and disabled defaults for credential-gated providers.
- Phase 2 acceptance criteria are met: fixture paths exist, JSON fixtures parse, Web of Science is declared as TSV, and provider registry/default settings agree.
- Phase 3 expected tests and docs exist: `tests/test_provider_registry.py`, ingestion coverage in `tests/test_polars_jiter_ingestion.py`, this verification record, and `review.md`.
- Phase 3 acceptance criteria are met locally. The only remaining step is the archive commit after this verification commit passes GitHub Actions.
- No unrelated implementation files were modified for this closeout.

## Local Evidence

- `uv run --group dev pytest tests/test_provider_registry.py -q`: passed, `7 passed` before fixture-contract fixes.
- `uv run --group dev pytest tests/test_provider_registry.py tests/test_polars_jiter_ingestion.py -q`: passed, `26 passed`.
- `uv lock --check`: passed.
- `uv run --group dev pytest tests -q`: passed, `71 passed`.
- `uv run --group dev ruff check pybibx/providers pybibx/ingestion pybibx/schemas tests/test_provider_registry.py tests/test_polars_jiter_ingestion.py`: passed.
- `uv run --group dev ruff check pybibx setup.py tests`: passed.
- `uv run --group dev ruff format --check pybibx setup.py tests`: passed.
- `uv run --group dev pyright`: passed with 0 errors, 0 warnings, and 0 informations.
- `uv run --group dev ty check pybibx/__init__.py`: passed.
- `python scripts/conductor_swarm.py validate-config --json`: passed.
- `python scripts/conductor_swarm.py plan --json`: passed and preserved the Codex fallback lane while Cline remains non-TTY blocked.
- `vale conductor README.md`: passed with 0 errors and 0 warnings; existing docs produce spelling suggestions only.
- Deputy read-only checks: `git diff --check` passed and `python scripts/check_conductor_swarm.py` passed.
- Verification commit `54970f2ca21e2a70dc71fd49ca2c13966bdae234` passed GitHub Actions `quality` run `28072417078`.

## Review Evidence

- Implementation-coverage reviewer found no remaining blockers after the ORCID/settings fix and confirmed all requested providers, settings parity, fixture existence, JSON parsing, and credential/export boundaries.
- Fixture-contract reviewer found three blockers that were fixed: Web of Science TSV format drift, provider endpoint response-format ambiguity, and stale OpenCitations API metadata.
- Deputy reviewer found closeout blockers that were fixed or queued for archive: stale verification evidence, missing review evidence, thin phase checkpoints, and active registry state.

## Known Boundaries

- This track does not implement live HTTP clients, provider adapters, retries, pagination, or credential loading.
- Provider URLs and terms notes are registry metadata for the next adapter track; each live adapter must verify current provider documentation and terms before use.
- Credential-gated providers remain disabled by default.
