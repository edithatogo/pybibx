# Verification

Local verification refreshed on 2026-06-24.

## Commands

- `uv lock --check`
- `uv run --group dev pytest tests/test_ontology_graph_core.py tests/test_schema_settings_versioning.py -q`
- `uv run --group dev ruff check pybibx/graph/builders.py pybibx/schemas/records.py pybibx/schemas/ontology.py pybibx/__init__.py tests/test_ontology_graph_core.py`
- `uv run --group dev pyright pybibx/graph/builders.py pybibx/schemas/records.py pybibx/schemas/ontology.py pybibx/__init__.py tests/test_ontology_graph_core.py`
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

- `uv lock --check`: resolved 445 packages.
- Targeted ontology/schema tests: 17 passed.
- Targeted Ruff and Pyright checks: passed.
- Full test suite: 83 passed.
- `ruff check`: all checks passed.
- `ruff format --check`: 32 files already formatted.
- `pyright`: 0 errors, 0 warnings, 0 informations.
- `ty`: all checks passed.
- `check_conductor_swarm.py`: conductor swarm smoke ok.
- `conductor_swarm.py validate-config --json`: status ok.
- `conductor_swarm.py plan --json`: active fallback is `codex_swarm_fallback`.
- `git diff --check`: no whitespace errors.
- `vale conductor README.md`: 0 errors and 0 warnings; suggestions only.

## Review Fixes

- Preserved parallel semantic citation edges in NetworkX export with `nx.MultiDiGraph`.
- Rejected duplicate co-authorship `work_id` inputs to avoid inflated shared-publication weights.
- Rejected repeated unidentified same-name authors without ORCID to avoid silent identity collapse.
- Added ORCID check digit validation.
- Added ontology compatibility stamps to additive ontology bundles.
- Kept modern graph imports independent from `pybibx.base.pbx` and pandas-heavy legacy runtime imports.

## Phase Checkpoints

- Expected files exist: ontology schema models, graph builders, public package exports, tests, verification evidence, review evidence, and metadata.
- Unrelated modifications: none intentionally made outside the ontology graph contract, lazy package-root compatibility fix, and Conductor evidence for this track.
- Acceptance criteria: DOI/ROR/ORCID validation is fail-closed; citation graphs preserve CiTO intent, context, evidence IDs, and weights; co-authorship graphs aggregate repeated shared publications while rejecting duplicate inputs; NetworkX export preserves node and edge attributes including parallel citation edges.
- Schema snapshot check: covered by `model_json_schema_snapshot(Work)` and additive ontology bundle version-stamp assertions in the schema/ontology tests.
- Scalene: not run for this closeout because the fixes are contract and validation changes, not a performance-sensitive graph algorithm rewrite. The performance profiler remains available in the dev group for future graph scaling work.
- Cline/DeepSeek lane: blocked by non-TTY `cline config --json`; Codex subagents were used as the workflow-defined fallback.
- Blockers: none pending local validation and remote CI.

## Remote CI

- Pending final closeout commit and GitHub Actions run.
