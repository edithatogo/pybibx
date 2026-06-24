# Verification

Local verification refreshed on 2026-06-24.

## Commands

- `uv lock --check`
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

- Targeted tests: `uv run --group dev pytest tests/test_quality_observability_perf.py tests/test_packaging_tooling.py -q`: 12 passed.
- `pytest`: 91 passed.
- `ruff check`: all checks passed.
- `ruff format --check`: 32 files already formatted.
- `pyright`: 0 errors, 0 warnings, 0 informations.
- `ty`: all checks passed.
- `check_conductor_swarm.py`: conductor swarm smoke ok.
- `conductor_swarm.py validate-config --json`: status ok.
- `conductor_swarm.py plan --json`: active fallback is Codex swarm because Cline remains blocked by non-TTY configuration.
- `git diff --check`: no whitespace errors.
- `vale conductor README.md`: 0 errors, 0 warnings; existing project-spelling suggestions only.
- GitHub Actions `quality`: passed on pushed commit `b325f65ff11f2ccf391a5438114c97624535c6ca`.
  Run: https://github.com/edithatogo/pybibx/actions/runs/28074505146

## Scope Notes

- Added optional quality dependency lane for Great Expectations, Deepchecks, and Kedro.
- Added typed data-quality suites, Kedro pipeline specs, observability plans, Scalene profile specs, and pytest-gremlins specs.
- Added Pixi task discovery for mutation and profiling lanes.
- Refreshed provider-fixture suite coverage, optional lane gating, Kedro graph validation, and quality import-boundary tests during review.
- Did not make optional quality/observability packages mandatory for baseline imports.
- Did not execute expensive Scalene profiles or pytest-gremlins mutation runs in the default local or CI gate.

## Manual Checkpoint

- Expected code paths: `pybibx/quality/lanes.py`, `pixi.toml`, `tests/test_quality_observability_perf.py`, and `tests/test_packaging_tooling.py`.
- Expected docs: track index, review, and verification are updated with acceptance evidence.
- Unrelated files: none intentionally changed.
- Acceptance: all spec bullets are mapped in `review.md` and covered by local gates plus remote CI.
- Blockers: Cline/DeepSeek remains blocked by non-TTY config, so Codex subagents were used; no repository-local blocker remains.
