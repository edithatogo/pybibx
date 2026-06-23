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

- `pytest`: 58 passed.
- `ruff check`: all checks passed.
- `ruff format --check`: 26 files already formatted.
- `pyright`: 0 errors, 0 warnings, 0 informations.
- `ty`: all checks passed.
- `check_conductor_swarm.py`: conductor swarm smoke ok.
- `git diff --check`: no whitespace errors.
- GitHub Actions `quality`: passed on pushed commit `e1ffbd7aab0a193fa69ff9860295088c404ee985`.
  Run: https://github.com/edithatogo/pybibx/actions/runs/28046960288

## Scope Notes

- Added optional AI orchestration contracts for PydanticAI, Instructor, DSPy, and LlamaIndex.
- Added local runtime configuration support for Ollama, mistral.rs, and explicit OpenAI-compatible endpoints.
- Added evidence-required task and extraction specs.
- Did not add live LLM calls, hosted LLM defaults, mandatory optional AI imports, or a Rig/Rust bridge in this track.
