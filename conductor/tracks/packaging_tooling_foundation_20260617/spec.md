# Packaging Tooling Foundation Specification

## Overview

Implement the first blocker identified by the swarm: modern packaging and quality-tooling scaffolding for the PyBibX 6.0 line, while keeping the current PyBibX 5.9.2 runtime behavior compatible.

## Requirements

- Add PEP 621 package metadata in `pyproject.toml`.
- Preserve the existing package name, version, console script, package data, long description, author metadata, and legacy import behavior.
- Keep `setup.py` as a compatibility shim instead of the metadata source of truth.
- Target CPython 3.14 for the 6.0 development lane, based on Python.org listing Python 3.14.6 as the latest stable release on 2026-06-16.
- Split optional dependency groups so web, visualization, NLP, AI, torch, RAG, graph, and development tools are not all mandatory.
- Add Pixi, uv workspace metadata, Ruff strict configuration, Pyright strict configuration, ty configuration, pytest/coverage configuration, Vale, Renovate, and GitHub Actions.
- Do not silently add ambiguous dependencies such as Una or externally gated services such as TestSprite.

## Out Of Scope

- Do not implement Pydantic schemas or provider adapters in this track.
- Do not remove legacy pandas, NetworkX, Flask, or AI APIs.
- Do not require hosted services or paid credentials.

## Acceptance Criteria

- `python -m build`-style metadata is represented in `pyproject.toml`; local validation can parse the file.
- Core dependencies reflect current eager imports; optional extras capture lazy/heavy stacks.
- Ruff, Pyright, ty, pytest, Vale, Renovate, and GitHub Actions configs are present.
- Swarm doctor and smoke checks still run.
- Track plan is updated and committed.

