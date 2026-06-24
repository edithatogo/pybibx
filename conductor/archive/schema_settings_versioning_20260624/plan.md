# Schema Settings Versioning Plan

## Phase 1: Contracts And Version Profiles

- [x] Task: Add maintained schema package.
    - [x] Create enums for providers, formats, ontology terms, work types, and export profiles.
    - [x] Create version-profile models for library, schemas, providers, inputs, outputs, ontology, and settings.
    - [x] Create base model helpers and JSON Schema snapshot helpers.
- [x] Task: Add bibliometric entity models.
    - [x] Create `Author`, `Institution`, `Work`, `Citation`, `OntologyFacet`, `EvidenceSet`, and `ExportManifest` models.
    - [x] Validate DOI, ORCID, ROR URL, dates, counts, and evidence consistency.
- [x] Task: Conductor - User Manual Verification 'Contracts And Version Profiles' (Protocol in workflow.md)

## Phase 2: Settings And Integration

- [x] Task: Add typed settings.
    - [x] Create provider, runtime, storage, observability, and feature-gate settings using `pydantic-settings`.
    - [x] Support environment-variable loading without requiring credentials.
- [x] Task: Integrate package metadata.
    - [x] Promote Pydantic dependencies to baseline dependencies.
    - [x] Expose maintained schema/settings APIs without changing legacy runtime behavior.
- [x] Task: Conductor - User Manual Verification 'Settings And Integration' (Protocol in workflow.md)

## Phase 3: Tests And Verification

- [x] Task: Add tests.
    - [x] Cover valid normalized records, invalid constraints, export manifests, JSON Schema snapshots, and environment settings.
    - [x] Keep tests independent of external APIs and credentials.
- [x] Task: Run quality gates.
    - [x] Run `uv lock --check`.
    - [x] Run Ruff check and format check.
    - [x] Run Pyright, ty, and pytest.
    - [x] Run Conductor swarm smoke.
- [x] Task: Complete and push.
    - [x] Record verification evidence.
    - [x] Mark track complete.
    - [x] Commit and push to `origin main`.
- [x] Task: Conductor - User Manual Verification 'Tests And Verification' (Protocol in workflow.md)
