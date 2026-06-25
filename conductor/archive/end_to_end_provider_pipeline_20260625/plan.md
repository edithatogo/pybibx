# End-To-End Provider Pipeline Plan

## Phase 1: Pipeline Contract And Tests

- [x] Task: Define the provider pipeline public contract.
    - [x] Add tests for provider selection, input path handling, output format selection, and versioned pipeline results.
    - [x] Add tests that reject credential-gated or export-only providers when invoked as open providers.
    - [x] Add tests for invalid provider names, missing input files, and schema validation failures.
- [x] Task: Define deterministic fixture expectations.
    - [x] Select OpenAlex, Crossref, and PubMed/MEDLINE fixtures from the existing provider registry.
    - [x] Define expected normalized `Work` fields and compatibility metadata for each fixture.
    - [x] Keep fixture tests offline and independent of external credentials.
- [x] Task: Conductor - User Manual Verification 'Pipeline Contract And Tests' (Protocol in workflow.md)

## Phase 2: Headless Provider Pipeline

- [x] Task: Implement the provider pipeline module.
    - [x] Compose provider registry lookup, settings, Polars/Jiter parsers, and schema models.
    - [x] Preserve raw audit metadata and provider/input version stamps.
    - [x] Return immutable normalized results with deterministic ordering.
- [x] Task: Add export support for pipeline results.
    - [x] Emit JSONL normalized records.
    - [x] Emit CSL-JSON bibliography output.
    - [x] Include output version metadata and export manifests.
- [x] Task: Add a minimal CLI or documented Python API entry point.
    - [x] Ensure the entry point runs against local fixtures.
    - [x] Document provider access-mode boundaries in help text or examples.
- [x] Task: Conductor - User Manual Verification 'Headless Provider Pipeline' (Protocol in workflow.md)

## Phase 3: Validation And Evidence

- [x] Task: Run baseline-safe quality gates.
    - [x] Run `uv lock --check`.
    - [x] Run targeted provider pipeline tests.
    - [x] Run full pytest.
    - [x] Run Ruff check and format check.
    - [x] Run Pyright and ty.
    - [x] Run Conductor swarm smoke checks.
- [x] Task: Record implementation evidence.
    - [x] Add `verification.md` with commands, results, boundaries, and any deferred provider work.
    - [x] Add `review.md` after conductor review and fix loop.
    - [x] Commit, push, and confirm GitHub Actions quality passes.
- [x] Task: Conductor - User Manual Verification 'Validation And Evidence' (Protocol in workflow.md)
