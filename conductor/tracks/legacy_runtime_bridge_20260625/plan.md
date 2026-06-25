# Legacy Runtime Bridge Plan

## Phase 1: Compatibility Contract And Baseline Tests

- [x] Task: Map legacy input and output shapes.
    - [x] Identify the minimal dataframe columns needed for representative legacy analyses.
    - [x] Identify common legacy import/export columns that can map to maintained schema records.
    - [x] Document unsupported or ambiguous fields.
- [x] Task: Add bridge contract tests.
    - [x] Test maintained `Work` records to legacy dataframe conversion.
    - [x] Test legacy dataframe/export rows to maintained records.
    - [x] Test legacy import smoke behavior remains unchanged.
    - [x] Test unsupported paths produce explicit errors.
- [ ] Task: Conductor - User Manual Verification 'Compatibility Contract And Baseline Tests' (Protocol in workflow.md)

## Phase 2: Bridge Implementation

- [x] Task: Implement maintained-to-legacy adapters.
    - [x] Convert works, authors, institutions, citations, and source metadata into deterministic pandas-compatible structures.
    - [x] Preserve compatibility/version metadata where possible.
    - [x] Keep bridge code isolated from `pybibx/base` internals.
- [x] Task: Implement legacy-to-maintained adapters.
    - [x] Normalize legacy DOI, author, institution, year, and citation-count fields through Pydantic schemas.
    - [x] Handle malformed or partial legacy rows with clear validation errors.
    - [x] Add optional warnings or diagnostics for lossy conversions.
- [x] Task: Add migration documentation and examples.
    - [x] Show provider pipeline output feeding a legacy-compatible dataframe.
    - [x] Show legacy export rows converted into maintained records.
    - [x] State what remains unsupported.
- [ ] Task: Conductor - User Manual Verification 'Bridge Implementation' (Protocol in workflow.md)

## Phase 3: Validation And Evidence

- [x] Task: Run baseline-safe quality gates.
    - [x] Run `uv lock --check`.
    - [x] Run targeted bridge tests.
    - [x] Run full pytest.
    - [x] Run Ruff check and format check.
    - [x] Run Pyright and ty.
    - [x] Run Conductor swarm smoke checks.
- [x] Task: Record implementation evidence.
    - [x] Add `verification.md` with local checks, bridge coverage, and unsupported boundaries.
    - [ ] Add `review.md` after conductor review and fix loop.
    - [x] Commit, push, and confirm GitHub Actions quality passes.
- [ ] Task: Conductor - User Manual Verification 'Validation And Evidence' (Protocol in workflow.md)
