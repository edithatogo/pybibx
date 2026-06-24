# Verification

Local verification refreshed on 2026-06-24.

## Commands

- `uv lock --check`
- `uv run --group dev pytest tests/test_full_text_rag.py tests/test_ai_agent_layer.py tests/test_schema_settings_versioning.py -q`
- `uv run --group dev ruff check pybibx/rag/fulltext.py pybibx/rag/__init__.py tests/test_full_text_rag.py pyproject.toml`
- `uv run --group dev pyright pybibx/rag/fulltext.py pybibx/rag/__init__.py tests/test_full_text_rag.py`
- `uv run --group dev pytest tests -q`
- `uv run --group dev ruff check pybibx setup.py tests`
- `uv run --group dev ruff format --check pybibx setup.py tests`
- `uv run --group dev pyright`
- `uv run --group dev ty check pybibx/__init__.py`
- `python scripts/check_conductor_swarm.py`
- `python scripts/conductor_swarm.py validate-config --json`
- `python scripts/conductor_swarm.py plan --json`
- `git diff --check`
- `vale conductor README.md`

## Results

- `uv lock --check`: resolved 445 packages.
- Targeted RAG/AI/schema tests: 28 passed.
- Targeted Ruff and Pyright checks: passed.
- Full test suite: 88 passed.
- `ruff check`: all checks passed.
- `ruff format --check`: 32 files already formatted.
- `pyright`: 0 errors, 0 warnings, 0 informations.
- `ty`: all checks passed.
- `check_conductor_swarm.py`: conductor swarm smoke ok.
- `conductor_swarm.py validate-config --json`: status ok.
- `conductor_swarm.py plan --json`: active fallback is `codex_swarm_fallback`.
- `git diff --check`: no whitespace errors.
- `vale conductor README.md`: 0 errors and 0 warnings; suggestions only.

## Review Fixes

- Required direct HTTPS PDF URLs for Unpaywall full-text routes.
- Validated arXiv IDs/hosts and bioRxiv/medRxiv server identity.
- Added parser candidate and parsed-document contracts for Docling/PDFMux evaluation.
- Added source-scoped chunk IDs, nested Markdown section paths, and hard splitting for long sections.
- Added flat LanceDB-compatible vector records.
- Tightened grounded extractions to require quote-backed chunk evidence matching the extraction `work_id`.
- Rejected duplicate supporting chunk IDs and preserved support order.
- Narrowed the `rag` optional extra to parser/embed/store dependencies; PDFMux remains a terms-gated evaluation-only backend via `rag-pdfmux`.

## Phase Checkpoints

- Expected files exist: RAG route/parser/chunk/vector/evidence contracts, public exports, tests, verification evidence, review evidence, and metadata.
- Unrelated modifications: none intentionally made outside the full-text RAG contract, optional dependency metadata, tests, lockfile, and Conductor evidence for this track.
- Acceptance criteria: Unpaywall routes only direct OA PDF URLs; arXiv, bioRxiv, and medRxiv fixtures produce legal routes and reject spoofed/mismatched sources; Docling/PDFMux use a common parser contract; chunks preserve source locators and nested section context; embedding/vector records align by chunk ID and flatten for LanceDB; evidence-grounded extractions fail closed without concrete matching chunks.
- Schema snapshot check: covered by Pydantic model construction and `model_json_schema_snapshot(Work)` in the targeted schema tests; RAG-specific public schemas are exercised by direct model validation tests.
- Scalene: not run for this closeout because the fixes are schema/routing/validation changes, not performance-sensitive parser or vector-store execution.
- Cline/DeepSeek lane: blocked by non-TTY `cline config --json`; Codex subagents were used as the workflow-defined fallback.
- Blockers: none pending local validation and remote CI.

## Remote CI

- GitHub Actions `quality`: passed on pushed review-fix commit `bb8bb28ba9114c0017f8125b43e9cb2660b867cf`.
  Run: https://github.com/edithatogo/pybibx/actions/runs/28073673996
