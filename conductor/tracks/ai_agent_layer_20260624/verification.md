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

- Targeted tests: `uv run --group dev pytest tests/test_ai_agent_layer.py tests/test_full_text_rag.py tests/test_schema_settings_versioning.py -q`: 30 passed.
- `pytest`: 90 passed.
- `ruff check`: all checks passed.
- `ruff format --check`: 32 files already formatted.
- `pyright`: 0 errors, 0 warnings, 0 informations.
- `ty`: all checks passed.
- `check_conductor_swarm.py`: conductor swarm smoke ok.
- `conductor_swarm.py validate-config --json`: status ok.
- `conductor_swarm.py plan --json`: active fallback is Codex swarm because Cline remains blocked by non-TTY configuration.
- `git diff --check`: no whitespace errors.
- `vale conductor README.md`: 0 errors, 0 warnings; existing project-spelling suggestions only.
- GitHub Actions `quality`: pending for this closeout commit until pushed.

## Scope Notes

- Tightened optional AI orchestration contracts for PydanticAI, Instructor, DSPy, and LlamaIndex.
- Added local runtime configuration support for Ollama, mistral.rs metrics, and explicit OpenAI-compatible endpoints.
- Hosted OpenAI-compatible endpoints now require `enable_hosted_llms`.
- Added evidence-required task, extraction, and plan matching checks.
- Added backend-specific AI extras while keeping baseline imports dependency-free.
- Did not add live LLM calls, hosted LLM defaults, mandatory optional AI imports, or a Rig/Rust bridge in this track.

## Manual Checkpoint

- Expected code paths: `pybibx/ai/orchestration.py`, `pybibx/settings.py`, `pybibx/rag/fulltext.py`, `pyproject.toml`, `uv.lock`, and focused regression tests.
- Expected docs: track index, review, and verification are updated with acceptance evidence.
- Unrelated files: none intentionally changed.
- Acceptance: all spec bullets are mapped in `review.md` and covered by local gates.
- Blockers: Cline/DeepSeek remains blocked by non-TTY config, so Codex subagents were used; GitHub Actions evidence remains pending until push.
