# Legacy Runtime Bridge Plan

## Phase 1: Compatibility Contract And Baseline Tests

- [ ] Task: Map legacy input and output shapes.
    - [ ] Identify the minimal dataframe columns needed for representative legacy analyses.
    - [ ] Identify common legacy import/export columns that can map to maintained schema records.
    - [ ] Document unsupported or ambiguous fields.
- [ ] Task: Add bridge contract tests.
    - [ ] Test maintained `Work` records to legacy dataframe conversion.
    - [ ] Test legacy dataframe/export rows to maintained records.
    - [ ] Test legacy import smoke behavior remains unchanged.
    - [ ] Test unsupported paths produce explicit errors.
- [ ] Task: Conductor - User Manual Verification 'Compatibility Contract And Baseline Tests' (Protocol in workflow.md)

## Phase 2: Bridge Implementation

- [ ] Task: Implement maintained-to-legacy adapters.
    - [ ] Convert works, authors, institutions, citations, and source metadata into deterministic pandas-compatible structures.
    - [ ] Preserve compatibility/version metadata where possible.
    - [ ] Keep bridge code isolated from `pybibx/base` internals.
- [ ] Task: Implement legacy-to-maintained adapters.
    - [ ] Normalize legacy DOI, author, institution, year, and citation-count fields through Pydantic schemas.
    - [ ] Handle malformed or partial legacy rows with clear validation errors.
    - [ ] Add optional warnings or diagnostics for lossy conversions.
- [ ] Task: Add migration documentation and examples.
    - [ ] Show provider pipeline output feeding a legacy-compatible dataframe.
    - [ ] Show legacy export rows converted into maintained records.
    - [ ] State what remains unsupported.
- [ ] Task: Conductor - User Manual Verification 'Bridge Implementation' (Protocol in workflow.md)

## Phase 3: Validation And Evidence

- [ ] Task: Run baseline-safe quality gates.
    - [ ] Run `uv lock --check`.
    - [ ] Run targeted bridge tests.
    - [ ] Run full pytest.
    - [ ] Run Ruff check and format check.
    - [ ] Run Pyright and ty.
    - [ ] Run Conductor swarm smoke checks.
- [ ] Task: Record implementation evidence.
    - [ ] Add `verification.md` with local checks, bridge coverage, and unsupported boundaries.
    - [ ] Add `review.md` after conductor review and fix loop.
    - [ ] Commit, push, and confirm GitHub Actions quality passes.
- [ ] Task: Conductor - User Manual Verification 'Validation And Evidence' (Protocol in workflow.md)
