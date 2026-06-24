# Review

Automated review completed on 2026-06-24.

## Review Scope

- `conductor/tracks/full_text_rag_20260624/spec.md`
- `conductor/tracks/full_text_rag_20260624/plan.md`
- `conductor/workflow.md`
- `pybibx/rag/fulltext.py`
- `pybibx/rag/__init__.py`
- `pyproject.toml`
- `uv.lock`
- `tests/test_full_text_rag.py`

## Findings And Fixes

- Fixed Unpaywall routing to require direct HTTPS PDF URLs from `url_for_pdf`; OA landing pages and malformed/non-HTTPS URLs no longer enter local PDF RAG routes.
- Added arXiv ID/host validation and bioRxiv/medRxiv server-mismatch rejection.
- Added parser candidate validation so PDF parsing only targets legal, credential-free routes.
- Added a typed parser result/interface contract with `ParsedDocument` and `PdfParserAdapter`.
- Added source-scoped chunk identifiers and nested Markdown heading paths.
- Added hard splitting for long sentence-like sections so chunks respect `max_chars`.
- Added flat LanceDB-compatible vector records with top-level `id`, `vector`, text, locator, section, and backend metadata.
- Tightened grounded extraction evidence so claims require concrete quotes and chunk IDs tied to the extraction `work_id`.
- Rejected duplicate supporting chunk IDs and preserved caller support order.
- Narrowed the optional `rag` extra to parser/embed/store dependencies; LLM/agent frameworks remain in the `ai`, `modern`, and `all` extras. PDFMux remains evaluation-only under a terms-gated empty `rag-pdfmux` extra until a package contract is approved.

## Validation

- Targeted tests: `uv run --group dev pytest tests/test_full_text_rag.py tests/test_ai_agent_layer.py tests/test_schema_settings_versioning.py -q` passed with 28 tests.
- Targeted lint: `uv run --group dev ruff check pybibx/rag/fulltext.py pybibx/rag/__init__.py tests/test_full_text_rag.py pyproject.toml` passed.
- Targeted type check: `uv run --group dev pyright pybibx/rag/fulltext.py pybibx/rag/__init__.py tests/test_full_text_rag.py` passed.

## Remaining Blockers

- None after the fixes above. Full-suite and remote CI evidence is recorded in `verification.md`.
