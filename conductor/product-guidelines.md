# Product Guidelines

## Compatibility

- Preserve current PyBibX workflows through explicit legacy adapters while planning the 6.0 internal refactor.
- Avoid silently changing scientific results. Any metric change must be versioned, documented, and covered by fixtures.
- Keep paid, credentialed, or hosted services optional. Open/local workflows must remain viable.

## Scientific Integrity

- Treat provider provenance as first-class data.
- Every AI-generated claim must trace back to evidence IDs, source records, and citation metadata.
- Never scrape Google Scholar by default; accept user-exported BibTeX/RIS/CSL-style inputs instead.
- Separate open providers from credential-gated providers in settings, docs, and tests.

## Developer Experience

- Prefer strict, typed, small modules over monolithic data-processing functions.
- Use Pydantic models and JSON Schema snapshots to make API changes explicit.
- Use Polars lazy/streaming dataframes for ingestion and tabular transforms.
- Keep Rust-backed libraries behind clear Python interfaces and optional extras.

## Documentation Style

- Document current state and target state separately.
- Use MoSCoW priorities for requirements.
- Use Mermaid diagrams for data flow, schema gates, agent loops, and CI/tooling.
- Keep track plans executable, with unchecked task markers for every task and subtask.

