# Verification

Local verification completed on 2026-06-23 UTC:

- `uv lock --check`: passed
- `uv run --group dev pytest tests -q`: 69 passed
- `uv run --group dev ruff check pybibx setup.py tests`: passed
- `uv run --group dev ruff format --check pybibx setup.py tests`: passed
- `uv run --group dev pyright`: 0 errors, 0 warnings, 0 informations
- `uv run --group dev ty check pybibx/__init__.py`: passed
- `python scripts/check_conductor_swarm.py`: passed
- `git diff --check`: passed

Remote verification:

- GitHub Actions `quality` for commit `4757000d5eb6f053f37681b94ec45bf262dab7ad`: passed
- Run ID: `28047783873`
- URL: `https://github.com/edithatogo/pybibx/actions/runs/28047783873`
