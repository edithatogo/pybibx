# Swarm Phase 1 Evidence: Repository And Tooling Foundation

Agent: `019ecba7-2cba-7290-8eba-2bd48cc49a47`

## Findings

- Current packaging is still `setup.py` only, with version `5.9.2` and a monolithic dependency list.
- No `pyproject.toml`, `pixi.toml`, `uv.lock`, Ruff, Pyright, Vale, Renovate, or GitHub Actions configuration exists yet.
- The 6.0 tooling migration should be `pyproject.toml` first, while preserving current package identity and legacy compatibility.

## Implementation Shape

- Add Pixi as the environment and task layer.
- Add uv workspace/project metadata in `pyproject.toml`.
- Use explicit latest-stable CPython target for the 6.0 line, with dependency blockers documented if resolution fails.
- Split dependencies into minimal core plus extras: `web`, `viz`, `nlp`, `ai`, `torch`, `legacy`, `rag`, `graph`, and `dev`.
- Add strict Ruff, Pyright, ty, pytest, coverage, pytest-gremlins, Vale, Scalene, Renovate, Ruff Action, and optional TestSprite lanes.
- Keep Una as verify-before-pinning.

## Acceptance Criteria

- Core import does not require torch, web, AI, or RAG dependencies.
- CI/tool config exists for linting, typing, testing, prose, dependency updates, and selected performance checks.
- TestSprite and Una are documented as optional/external or deferred until verified.

## Blockers

- CPython latest-stable target may expose incompatibilities in torch, numba, and NLP dependencies.
- TestSprite needs external account/app verification.
- Una project fit remains ambiguous.

