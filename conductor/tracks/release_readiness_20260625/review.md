# Release Readiness Review

## Review Findings

### Fixed

- The release surface documented public, provisional, optional, and legacy areas but did not explicitly mark any internal module boundary.
- The new `pybibx.release` module was used by tests and docs but was not itself listed in the machine-readable release surface.
- Credential-gated provider status was documented in prose but not represented in the optional-extra compatibility contract.

## Fixes Applied

- Added `pybibx.release` as a public alpha surface in the release-readiness contract and docs.
- Added `pybibx.base.*` as an internal legacy implementation boundary.
- Added `licensed-providers` as a credential-gated compatibility row for Scopus and Web of Science.
- Expanded release-readiness tests to assert public, internal, optional, legacy, blocked, and credential-gated classifications.

## Validation

- `uv run --group dev pytest tests/test_release_readiness.py -q` - pass, 5 tests.
- `uv lock --check` - pass.
- `uv run --group dev pytest tests -q` - pass, 109 tests.
- `uv run --group dev ruff check pybibx setup.py tests` - pass.
- `uv run --group dev ruff format --check pybibx setup.py tests` - pass.
- `uv run --group dev pyright` - pass, 0 errors.
- `uv run --group dev ty check pybibx/__init__.py pybibx/release.py` - pass.
- `uv run --group dev python -m build --wheel` - pass.
- `vale docs conductor README.md` - pass with suggestions only.
- `python scripts/check_conductor_swarm.py` - pass.
- `python scripts/conductor_swarm.py validate-config --json` - pass.
- `python scripts/conductor_swarm.py plan --json` - pass.
