# Release Readiness Verification

## Implementation Evidence

- Added `pybibx.release` release-readiness contract for the PyBibX 6.0 alpha boundary.
- Added release docs:
  - `docs/release-readiness.md`
  - `docs/migration-5.9.2-to-6-alpha.md`
- Added release-readiness tests in `tests/test_release_readiness.py`.
- Added explicit `pybibx.settings.__all__` for the public alpha settings surface.

## Local Package Checks

- `rm -rf dist build pybibx.egg-info && uv run --group dev python -m build --wheel` - pass.
- Import smoke with `pybibx`, package metadata, and `release_readiness_contract()` - pass.
- Wheel output `pybibx-5.9.2-py3-none-any.whl` was generated as evidence, then removed from source control.
- Build warning recorded: setuptools reports deprecated TOML table form for `project.license`; this is not failing today but should be modernized before the 2027-Feb-18 cutoff.

## Local Quality Checks

- `uv lock --check` - pass.
- `uv run --group dev pytest tests/test_release_readiness.py -q` - pass, 5 tests.
- `uv run --group dev pytest tests -q` - pass, 109 tests.
- `uv run --group dev ruff check pybibx setup.py tests` - pass.
- `uv run --group dev ruff format --check pybibx setup.py tests` - pass.
- `uv run --group dev pyright` - pass, 0 errors.
- `uv run --group dev ty check pybibx/__init__.py pybibx/release.py` - pass.
- `vale docs conductor README.md` - pass with suggestions only.
- `python scripts/check_conductor_swarm.py` - pass.
- `python scripts/conductor_swarm.py validate-config --json` - pass.
- `python scripts/conductor_swarm.py plan --json` - pass.

## Remaining External And Manual Gates

- PyPI publishing and tag creation are out of scope without explicit maintainer instruction.
- Scopus and Web of Science live connectors remain credential-gated.
- Google Scholar remains export/import-only; default scraping is unsupported.
- Cline with `deepseek-v4-flash` remains blocked from this non-TTY Codex session.
- Hosted LLMs, Reflex, Cosmograph, Rig, Graphina, PyG, PDFMux, and Monty are not production-ready claims unless separately verified.

## Remote Checks

- GitHub Actions `quality` run `28157796294` for commit `054197215ff2661a55128bf0fbf09d61aa508227` - pass.
