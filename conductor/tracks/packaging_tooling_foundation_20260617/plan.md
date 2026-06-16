# Packaging Tooling Foundation Plan

## Phase 1: Package Metadata And Dependency Split

- [x] Task: Add PEP 621 packaging metadata.
    - [x] Create `pyproject.toml`.
    - [x] Preserve package name, version, author, license metadata, README, package discovery, package data, and console script.
    - [x] Convert `setup.py` to a compatibility shim.
- [x] Task: Split dependencies.
    - [x] Keep eager-import legacy dependencies in core.
    - [x] Move web, visualization, NLP, AI, torch, RAG, graph, and dev dependencies into extras/groups.
    - [x] Document external/deferred lanes for Una and TestSprite.
- [x] Task: Conductor - User Manual Verification 'Package Metadata And Dependency Split' (Protocol in workflow.md)

## Phase 2: Tool Configuration

- [x] Task: Add quality tooling config.
    - [x] Configure Ruff strict linting and formatting.
    - [x] Configure Pyright strict mode with legacy exclusions.
    - [x] Configure ty, pytest, coverage, and pytest-gremlins entry points.
    - [x] Configure Vale and Renovate.
- [x] Task: Add environment and CI config.
    - [x] Add Pixi environment/tasks.
    - [x] Add uv workspace metadata.
    - [x] Add GitHub Actions for Ruff, typing, and tests.
- [x] Task: Conductor - User Manual Verification 'Tool Configuration' (Protocol in workflow.md)

## Phase 3: Verification And Push

- [x] Task: Run local validation.
    - [x] Parse `pyproject.toml`.
    - [x] Run swarm smoke checks.
    - [x] Run syntax/whitespace checks.
    - [x] Record known blockers.
- [x] Task: Commit and push.
    - [x] Commit track changes.
    - [x] Push to `origin main`.
- [x] Task: Conductor - User Manual Verification 'Verification And Push' (Protocol in workflow.md)
