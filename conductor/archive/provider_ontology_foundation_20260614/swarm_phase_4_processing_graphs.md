# Swarm Phase 4 Evidence: Processing, Graphs, And Data Quality

Agent: local Codex fallback after Phase 4 worker timeout.

## Findings

- Current code is pandas-heavy in `pybibx/base/openalex.py`, `batch.py`, `tsg.py`, `advanced.py`, and `pbx.py`.
- Current graph work uses NetworkX in temporal scholarly graph and advanced metrics paths.
- The target is Polars-first ingestion, RustWorkX-first graph computation, NetworkX export compatibility, and data quality checks through Kedro, Great Expectations, and Deepchecks.

## Implementation Shape

- Add a Polars ingestion layer for CSV, JSON, JSONL, BibTeX/RIS-derived tables, OpenAlex snapshots, and provider fixtures.
- Keep pandas only at legacy compatibility and user-facing dataframe boundaries.
- Add RustWorkX graph builders for citation, co-citation, bibliographic coupling, co-authorship, institution, country, and semantic CiTO edges.
- Preserve NetworkX export for users and downstream tooling.
- Evaluate Graphina, PyBiblioNet, and PyG in later tracks after RustWorkX parity exists.
- Add Kedro-style pipeline structure only after schema/provider contracts are stable.
- Use Great Expectations for provider/schema validation suites and Deepchecks for data/model quality checks.

## Acceptance Criteria

- Polars fixtures reproduce current OpenAlex and sample bibliographic outputs.
- RustWorkX graph metrics match current NetworkX results on small fixtures where algorithms overlap.
- Legacy dataframe outputs remain available.
- Data quality gates fail with clear provider/schema errors.

## Blockers

- Pydantic schema contracts and provider registry are prerequisites.
- No Polars or RustWorkX dependencies are currently declared.
- NetworkX parity fixtures are needed before replacing graph internals.
- Phase 4 sub-agent timed out twice, so this brief was produced by the orchestrator from local inspection.

