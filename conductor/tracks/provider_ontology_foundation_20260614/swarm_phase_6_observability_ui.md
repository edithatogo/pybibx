# Swarm Phase 6 Evidence: Observability, UI, And Reporting

Agent: `019ecba7-c19d-7ce0-98b7-27cc06a7a2b9`

## Findings

- Current UI is Flask-first and exposes many `/api/*` JSON endpoints via `pybibx/base/app.py`.
- The web-app entry points `pybibx.web_app()` and `pybibx.web_stop()` must remain compatible.
- No logging/observability abstraction or typed settings/feature gates exist yet.

## Implementation Shape

- Use Loguru for local structured logging in core, API, and agent boundaries.
- Use Logfire and OpenTelemetry optionally for traces, metrics, validation analytics, and agent/eval monitoring.
- Use Prometheus only when local runtime or API metrics are enabled.
- Keep Mantra verify-before-pinning; current evidence does not identify the intended package.
- Add FastAPI as the new typed service surface with versioned request/response models.
- Preserve Flask compatibility during migration.
- Evaluate Reflex and Cosmograph, benchmarked against current Temporal Scholarly Graph output.
- Implement PapersFlow-style citation-safe report manifests, not generic unsupported prose generation.
- Use BGBH/Country as a benchmark for geospatial country collaboration maps.

## Acceptance Criteria

- Core import does not require hosted observability, Reflex, Cosmograph, or Prometheus.
- `/metrics` is feature-gated.
- Report claims carry evidence IDs, source records, citation metadata, and generation metadata.
- Flask entry points continue to work while FastAPI is introduced.

## Blockers

- Pydantic schemas and settings are prerequisites.
- Global mutable Flask state needs migration strategy.
- Mantra identity remains unresolved.
- Benchmark fixtures are needed for BGBH/Country and Cosmograph scale tests.

