# Provider Registry Fixtures Plan

## Phase 1: Registry Contracts

- [x] Task: Add provider registry models.
    - [x] Define provider access modes and capabilities.
    - [x] Define provider endpoint, fixture, spec, and registry models.
    - [x] Add registry query helpers for access modes, capabilities, endpoints, and fixture paths.
- [x] Task: Populate default registry.
    - [x] Register open API providers.
    - [x] Register preprint providers.
    - [x] Register Google Scholar as export/import-only.
    - [x] Register Scopus and Web of Science as credential-gated.
- [x] Task: Conductor - User Manual Verification 'Registry Contracts' (Protocol in workflow.md)

## Phase 2: Fixtures And Settings

- [x] Task: Add static fixtures.
    - [x] Add JSON fixtures for open providers and preprint providers.
    - [x] Add BibTeX/CSV/tabular fixtures for export-only and credential-gated sources.
- [x] Task: Integrate settings.
    - [x] Add default provider settings for all registered providers.
    - [x] Preserve disabled defaults for credential-gated providers.
- [x] Task: Conductor - User Manual Verification 'Fixtures And Settings' (Protocol in workflow.md)

## Phase 3: Verification

- [x] Task: Add tests.
    - [x] Test registration coverage and uniqueness.
    - [x] Test access-mode boundaries.
    - [x] Test fixture existence and JSON parsing.
    - [x] Test settings integration.
- [x] Task: Run quality gates.
    - [x] Run Ruff check and format check.
    - [x] Run Pyright, ty, and pytest.
    - [x] Run Conductor swarm smoke.
- [x] Task: Complete and push.
    - [x] Record verification evidence.
    - [x] Mark track complete.
    - [x] Commit and push to `origin main`.
- [x] Task: Conductor - User Manual Verification 'Verification' (Protocol in workflow.md)
