# End-To-End Provider Pipeline Plan

## Phase 1: Pipeline Contract And Tests

- [ ] Task: Define the provider pipeline public contract.
    - [ ] Add tests for provider selection, input path handling, output format selection, and versioned pipeline results.
    - [ ] Add tests that reject credential-gated or export-only providers when invoked as open providers.
    - [ ] Add tests for invalid provider names, missing input files, and schema validation failures.
- [ ] Task: Define deterministic fixture expectations.
    - [ ] Select OpenAlex, Crossref, and PubMed/MEDLINE fixtures from the existing provider registry.
    - [ ] Define expected normalized `Work` fields and compatibility metadata for each fixture.
    - [ ] Keep fixture tests offline and independent of external credentials.
- [ ] Task: Conductor - User Manual Verification 'Pipeline Contract And Tests' (Protocol in workflow.md)

## Phase 2: Headless Provider Pipeline

- [ ] Task: Implement the provider pipeline module.
    - [ ] Compose provider registry lookup, settings, Polars/Jiter parsers, and schema models.
    - [ ] Preserve raw audit metadata and provider/input version stamps.
    - [ ] Return immutable normalized results with deterministic ordering.
- [ ] Task: Add export support for pipeline results.
    - [ ] Emit JSONL normalized records.
    - [ ] Emit CSL-JSON bibliography output.
    - [ ] Include output version metadata and export manifests.
- [ ] Task: Add a minimal CLI or documented Python API entry point.
    - [ ] Ensure the entry point runs against local fixtures.
    - [ ] Document provider access-mode boundaries in help text or examples.
- [ ] Task: Conductor - User Manual Verification 'Headless Provider Pipeline' (Protocol in workflow.md)

## Phase 3: Validation And Evidence

- [ ] Task: Run baseline-safe quality gates.
    - [ ] Run `uv lock --check`.
    - [ ] Run targeted provider pipeline tests.
    - [ ] Run full pytest.
    - [ ] Run Ruff check and format check.
    - [ ] Run Pyright and ty.
    - [ ] Run Conductor swarm smoke checks.
- [ ] Task: Record implementation evidence.
    - [ ] Add `verification.md` with commands, results, boundaries, and any deferred provider work.
    - [ ] Add `review.md` after conductor review and fix loop.
    - [ ] Commit, push, and confirm GitHub Actions quality passes.
- [ ] Task: Conductor - User Manual Verification 'Validation And Evidence' (Protocol in workflow.md)
