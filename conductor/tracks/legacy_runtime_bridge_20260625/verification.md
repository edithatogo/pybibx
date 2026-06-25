# Legacy Runtime Bridge Verification

## Implementation Evidence

- Added isolated bridge package: `pybibx.legacy`.
- Added maintained-to-legacy adapter: `works_to_legacy_dataframe`.
- Added legacy-to-maintained adapters: `legacy_dataframe_to_works` and `legacy_dataframe_to_export_manifest`.
- Added typed fail-closed boundary: `LegacyBridgeError` and `require_supported_legacy_analysis`.
- Added migration notes: `migration.md`.
- Added regression coverage: `tests/test_legacy_runtime_bridge.py`.

## Supported Runtime Boundary

The bridge emits a deterministic pandas dataframe shape for the existing `pbx_probe(data=..., db="scopus")`
path without modifying `pybibx/base`.

Supported bridge-fed legacy analysis surfaces:

- `author_counts`
- `citation_counts`
- `document_ids`
- `eda_report`
- `keyword_counts`
- `source_counts`

Unsupported paths fail with `LegacyBridgeError` or remain documented limitations:

- full-text RAG and semantic citation-intent extraction
- live provider ingestion
- GPU time-travel graph visualization
- workflows needing raw provider columns not represented in maintained `Work` records

## Local Checks

- `uv lock --check` - pass
- `uv run --group dev pytest tests/test_legacy_runtime_bridge.py -q` - pass, 5 tests
- `uv run --group dev pytest tests -q` - pass, 104 tests
- `uv run --group dev ruff check pybibx setup.py tests` - pass
- `uv run --group dev ruff format --check pybibx setup.py tests` - pass
- `uv run --group dev pyright` - pass, 0 errors
- `uv run --group dev ty check pybibx/__init__.py pybibx/legacy` - pass
- `python scripts/check_conductor_swarm.py` - pass
- `python scripts/conductor_swarm.py validate-config --json` - pass
- `python scripts/conductor_swarm.py plan --json` - pass
