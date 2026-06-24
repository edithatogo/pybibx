# Packaging Tooling Foundation Verification

Verified at `2026-06-24T02:56:01Z`.

## Implementation Evidence

- `pyproject.toml` is the PEP 621 metadata source of truth and preserves the `pybibx` package name, `5.9.2` version, README, author metadata, package data, console script, and package discovery.
- `setup.py` remains as a compatibility shim.
- Core dependencies match the legacy eager import surface; heavy and optional stacks are split into extras for web, visualization, NLP, AI, torch, RAG, graph, quality, observability, UI, reports, modern, legacy, and all.
- `pixi.toml`, `uv.lock`, uv workspace metadata, Ruff, Pyright, ty, pytest, coverage, pytest-gremlins, Scalene, Vale, Renovate, and GitHub Actions quality wiring are present.
- `conductor/dependency-policy.md` records that `uv sync --all-extras --group dev` is not baseline-safe on Python 3.14 because legacy `gensim` fails to build; CI intentionally uses `uv sync --group dev`.
- Una and TestSprite remain documented as external/deferred lanes rather than silently adding ambiguous or credential-bound packages.
- The Python target is CPython 3.14, based on the specification's Python.org check dated `2026-06-16`.

## Manual Checkpoints

- Phase 1 expected files and settings exist: `pyproject.toml`, `setup.py`, optional dependency groups, uv workspace metadata, and package data declarations.
- Phase 2 expected files and settings exist: `pixi.toml`, `pyrightconfig.json`, `.vale.ini`, `renovate.json`, `.github/workflows/quality.yml`, Ruff config, ty config, pytest config, coverage config, and dev dependency group.
- Phase 3 expected verification and push evidence exists: local gates are recorded below, the previous packaging CI fix is superseded by later successful `quality` runs, and the current track review is captured in `review.md`.
- No unrelated implementation files were modified for this closeout beyond the ty configuration and its packaging regression assertion.
- Acceptance criteria are met locally. Remaining boundaries are documented separately and are not archive blockers.

## Local Evidence

- `uv lock --check`: passed.
- `uv run --group dev pytest tests/test_packaging_tooling.py -q`: passed, `5 passed`.
- `uv run --group dev pytest tests -q`: passed, `70 passed` in deputy verification.
- `uv run --group dev ruff check pybibx setup.py tests`: passed.
- `uv run --group dev ruff format --check pybibx setup.py tests`: passed.
- `uv run --group dev pyright`: passed in deputy verification.
- `uv run --group dev ty check pybibx/__init__.py`: passed.
- `uv run --group dev python -m build --wheel`: passed in implementation-coverage verification; it reports the current setuptools future deprecation warning for table-form `project.license`.
- `python scripts/check_conductor_swarm.py`: passed in deputy verification.
- `git diff --check`: passed in deputy verification.
- `vale conductor README.md`: passed with 0 errors and 0 warnings in deputy verification.

## Remote Evidence

- GitHub Actions `quality` run `27626085039` previously failed during `uv sync --all-extras --group dev` because legacy extra `gensim==4.4.0` does not build against CPython 3.14.
- The workflow was corrected to baseline `uv sync --group dev`; the all-extras path remains explicit and non-baseline.
- Superseding `quality` run `27626228033` passed for the packaging baseline fix commit `d8796d6`.
- Current `main` also has successful `quality` run `28071672119` for commit `c323534e0172e6a2086b9e9149cd00e1bcf63076`.

## Known Boundaries

- The current 5.9.2 runtime remains legacy and is fenced under `pybibx/base`; this track adds strict tooling without rewriting the legacy analytics engine.
- `uv sync --all-extras --group dev` is not part of the baseline archive gate until legacy extras are Python 3.14-safe.
- Cline DeepSeek swarm launch remains blocked in this non-TTY session because `cline config --json` reports `interactive mode requires a TTY`; Codex subagents were used as the fallback worker lane.
- Una and TestSprite are documented as external/deferred lanes; no ambiguous package or credential-bound hosted service was added silently.
