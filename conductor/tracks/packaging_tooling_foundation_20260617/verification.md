# Packaging Tooling Foundation Verification

Verified at `2026-06-16T14:44:20Z`.

## Local Evidence

- `python - <<'PY' ... tomllib/json parse ...`: passed for `pyproject.toml`, `pixi.toml`, `pyrightconfig.json`, and `renovate.json`.
- `uv lock --python 3.14`: passed and generated `uv.lock` with CPython 3.14.5.
- `uv lock --check`: passed.
- `uv run --group dev ruff check pybibx setup.py tests`: passed.
- `uv run --group dev ruff format --check pybibx setup.py tests`: passed.
- `uv run --group dev pyright`: passed with strict mode on the maintained package surface.
- `uv run --group dev ty check pybibx/__init__.py`: passed.
- `uv run --group dev pytest tests -q`: passed, `4 passed`.
- `python scripts/check_conductor_swarm.py`: passed.
- `git diff --check`: passed.
- `vale conductor README.md`: passed with 0 errors and 0 warnings; existing docs produce spelling suggestions only.
- GitHub Actions run `27626085039`: failed during `uv sync --all-extras --group dev` because legacy extra `gensim==4.4.0` does not build against CPython 3.14. The baseline workflow now uses `uv sync --group dev`; all-extras remains an explicit non-baseline Pixi task.

## Known Boundaries

- The current 5.9.2 runtime remains legacy and is fenced under `pybibx/base`; this track adds strict tooling without rewriting the legacy analytics engine.
- Cline DeepSeek swarm launch remains blocked in this non-TTY session because `cline config --json` reports `interactive mode requires a TTY`.
- Una and TestSprite are documented as external/deferred lanes; no ambiguous package or credential-bound hosted service was added silently.
- The Python 3.14 target is based on Python.org listing Python 3.14.6 as the latest stable release on 2026-06-10.
