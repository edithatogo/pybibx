# Verification

Local verification refreshed on 2026-06-24:

- `uv lock --check`: passed
- `uv run --group dev pytest tests/test_ui_reports.py tests/test_packaging_tooling.py -q`: 11 passed
- `uv run --group dev pytest tests -q`: 92 passed
- `uv run --group dev ruff check pybibx setup.py tests`: passed
- `uv run --group dev ruff format --check pybibx setup.py tests`: 32 files already formatted
- `uv run --group dev pyright`: 0 errors, 0 warnings, 0 informations
- `uv run --group dev ty check pybibx/__init__.py`: passed
- `python scripts/check_conductor_swarm.py`: conductor swarm smoke ok
- `python scripts/conductor_swarm.py validate-config --json`: status ok
- `python scripts/conductor_swarm.py plan --json`: active fallback is Codex swarm because Cline remains blocked by non-TTY configuration
- `git diff --check`: passed
- `vale conductor README.md`: 0 errors, 0 warnings; existing project-spelling suggestions only

Remote verification:

- GitHub Actions `quality`: passed on pushed commit `6b8f7f1876309d1c4ebd044a3fd981a8bbd795f0`.
  Run: https://github.com/edithatogo/pybibx/actions/runs/28074844438

## Scope Notes

- Added maintained report/export contracts for citation-safe reports, BibLib-style Markdown notes, CSL-JSON export, and optional UI planning.
- Tightened report reference validation, citation evidence-chain validation, manifest evidence matching, and BibLib note collision handling during review.
- Did not add a live Reflex app, browser Cosmograph renderer, hosted PapersFlow API calls, or legacy Flask app changes.

## Manual Checkpoint

- Expected code paths: `pybibx/reports/exports.py`, `tests/test_ui_reports.py`, and packaging metadata/tests.
- Expected docs: track index, review, and verification are updated with acceptance evidence.
- Unrelated files: none intentionally changed.
- Acceptance: all spec bullets are mapped in `review.md` and covered by local gates plus remote CI.
- Blockers: Cline/DeepSeek remains blocked by non-TTY config, so Codex subagents were used; no repository-local blocker remains.
