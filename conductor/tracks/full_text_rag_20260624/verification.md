# Verification

Local verification completed on 2026-06-24.

## Commands

- `uv lock --check`
- `uv run --group dev pytest tests -q`
- `uv run --group dev ruff check pybibx setup.py tests`
- `uv run --group dev ruff format --check pybibx setup.py tests`
- `uv run --group dev pyright`
- `uv run --group dev ty check pybibx/__init__.py`
- `python scripts/check_conductor_swarm.py`
- `git diff --check`

## Results

- `pytest`: 51 passed.
- `ruff check`: all checks passed.
- `ruff format --check`: 23 files already formatted.
- `pyright`: 0 errors, 0 warnings, 0 informations.
- `ty`: all checks passed.
- `check_conductor_swarm.py`: conductor swarm smoke ok.
- `git diff --check`: no whitespace errors.
- GitHub Actions `quality`: passed on pushed commit `e28a6407a5bbd74606411bfcd2fb4f740f56a149`.
  Run: https://github.com/edithatogo/pybibx/actions/runs/28046616668

## Scope Notes

- Added legal full-text routing for Unpaywall and open preprint fixtures.
- Added Docling/PDFMux parser evaluation contracts without mandatory parser dependencies.
- Added FastEmbed-compatible embedding records and LanceDB-compatible vector records.
- Added evidence-grounded extraction contracts that fail closed when support chunks are absent.
- Did not add live full-text downloads, hosted parser calls, hosted LLM calls, or legacy runtime rewrites in this track.
