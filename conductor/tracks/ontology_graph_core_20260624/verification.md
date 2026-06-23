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

- `pytest`: 42 passed.
- `ruff check`: all checks passed.
- `ruff format --check`: 20 files already formatted.
- `pyright`: 0 errors, 0 warnings, 0 informations.
- `ty`: all checks passed.
- `check_conductor_swarm.py`: conductor swarm smoke ok.
- `git diff --check`: no whitespace errors.
- GitHub Actions `quality`: passed on pushed commit `607ec8384d34dca65c7c12b608d37975807be8ac`.
  Run: https://github.com/edithatogo/pybibx/actions/runs/28046214543

## Scope Notes

- Added maintained ontology models for CiTO, FaBiO, FRAPO, PSO, ORG, ROR, ORCID, and CSL.
- Added RustWorkX builders for semantic citation and co-authorship graphs.
- Added NetworkX export compatibility for downstream legacy and ecosystem users.
- Did not replace legacy plotting, historiograph, topic graph internals, RAG extraction, or live provider calls in this track.
