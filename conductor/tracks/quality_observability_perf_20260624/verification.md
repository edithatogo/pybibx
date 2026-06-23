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

- `pytest`: 64 passed.
- `ruff check`: all checks passed.
- `ruff format --check`: 29 files already formatted.
- `pyright`: 0 errors, 0 warnings, 0 informations.
- `ty`: all checks passed.
- `check_conductor_swarm.py`: conductor swarm smoke ok.
- `git diff --check`: no whitespace errors.

## Scope Notes

- Added optional quality dependency lane for Great Expectations, Deepchecks, and Kedro.
- Added typed data-quality suites, Kedro pipeline specs, observability plans, Scalene profile specs, and pytest-gremlins specs.
- Added Pixi task discovery for mutation and profiling lanes.
- Did not make optional quality/observability packages mandatory for baseline imports.
- Did not execute expensive Scalene profiles or pytest-gremlins mutation runs in the default local or CI gate.
