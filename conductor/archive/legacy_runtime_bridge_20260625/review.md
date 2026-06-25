# Legacy Runtime Bridge Review

## Review Findings

### Fixed

- The first implementation covered `Work`, `Author`, `Institution`, and export manifest conversion, but did not expose a
  maintained `Citation` adapter even though the track explicitly required citation conversion.

## Fixes Applied

- Added `citations` input support to `works_to_legacy_dataframe`, emitting deterministic legacy `references` values.
- Added `legacy_dataframe_to_citations` to convert representative legacy `references` columns into maintained `Citation`
  records.
- Added order-preserving duplicate reference removal when a citation matches both source work ID and source DOI.
- Expanded bridge tests and migration notes for citation conversion.

## Validation

- `uv run --group dev pytest tests/test_legacy_runtime_bridge.py -q` - pass, 5 tests
- `uv run --group dev ruff check pybibx setup.py tests` - pass
- `uv run --group dev ruff format --check pybibx setup.py tests` - pass
- `uv run --group dev pyright` - pass, 0 errors
- `uv run --group dev ty check pybibx/__init__.py pybibx/legacy` - pass
- `uv lock --check` - pass
- `uv run --group dev pytest tests -q` - pass, 104 tests
- `python scripts/check_conductor_swarm.py` - pass
- `python scripts/conductor_swarm.py validate-config --json` - pass
- `python scripts/conductor_swarm.py plan --json` - pass
