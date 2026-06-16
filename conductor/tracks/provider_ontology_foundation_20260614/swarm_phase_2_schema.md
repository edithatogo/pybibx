# Swarm Phase 2 Evidence: Schema, Settings, And Versioning

Agent: `019ecba7-4584-7ba3-ad18-930e71f1755e`

## Findings

- OpenAlex helpers normalize raw dicts/CSV into pandas dataframes and legacy PyBibX columns, but there is no typed Pydantic layer yet.
- Package version currently lives in `setup.py`; `pybibx/__init__.py` does not expose `__version__`.
- No settings layer exists for providers, local runtimes, storage, or observability.

## Implementation Shape

- Add `pybibx/schema/` with Pydantic v2 contracts for provider payloads, normalized works, authors, institutions, citations, evidence sets, reports, exports, and shared identifiers.
- Add `pybibx/settings.py` using `pydantic-settings`.
- Add `pybibx/version.py` for library, schema, provider adapter, ontology profile, and compatibility profile versions.
- Add OpenAlex raw payload models first, then compatibility adapters to current pandas/uppercase column layout.
- Commit JSON Schema snapshots for public contracts.
- Keep Jiter narrow: large JSON/JSONL streams and partial/streamed agent JSON only where it is measurably useful.

## Acceptance Criteria

- Version metadata appears on every normalized record and export envelope.
- Settings load from environment/config/overrides without requiring paid or hosted services.
- Compatibility adapters reproduce current OpenAlex dataframe columns.

## Blockers

- Phase 1 packaging is prerequisite for dependency and version source-of-truth cleanup.
- No provider fixture corpus exists yet.
- Exact schema versioning convention needs an implementation-track decision.

