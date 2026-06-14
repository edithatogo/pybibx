# Python Code Style Guide

## Defaults

- Use modern, typed Python targeting the latest stable CPython for PyBibX 6.0 code.
- Prefer small modules with explicit public exports over monolithic modules.
- Use Pydantic v2 models for public data contracts, settings, validation, serialization, and JSON Schema generation.
- Use Polars for new tabular ingestion and transformations.
- Use RustWorkX for new graph computation, with NetworkX only for compatibility/export paths.

## Checks

- Ruff is the formatting and linting authority.
- Pyright and ty must both pass for new strict modules.
- Tests should be deterministic, fixture-backed, and avoid network access unless explicitly marked.
- Provider API tests should use recorded/mocked responses by default.

## AI Boundaries

- AI outputs must validate into Pydantic models.
- Evidence-backed report claims must include source identifiers.
- Agentic workflows must fail closed when schemas, sources, or citations cannot be verified.

