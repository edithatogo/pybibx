# Release Readiness Plan

## Phase 1: Release Boundary And Tests

- [x] Task: Define release-readiness assertions.
    - [x] Add tests or checks for package metadata, wheel build, import smoke, and README/long-description health.
    - [x] Add checks that baseline dependency policy still avoids all-extras on Python 3.14.
    - [x] Add tests or scripts that fail closed if public API exports drift unexpectedly.
- [x] Task: Define the 6.0 alpha surface.
    - [x] Classify modules as public, provisional, optional, legacy, or internal.
    - [x] Identify docs/examples that must exist before alpha.
    - [x] Identify external blockers that must remain out of repo-local completion claims.
- [x] Task: Conductor - User Manual Verification 'Release Boundary And Tests' (Protocol in workflow.md)

## Phase 2: Documentation And Packaging Evidence

- [x] Task: Add release-readiness documentation.
    - [x] Add migration notes from PyBibX 5.9.2 to maintained 6.0 modules.
    - [x] Add optional-extra compatibility matrix.
    - [x] Add release notes covering completed tracks, limitations, and blockers.
    - [x] Add short examples for schema/settings, provider pipeline, legacy bridge, reports, and quality lanes where implemented.
- [x] Task: Refresh packaging and CI evidence.
    - [x] Run wheel build and import smoke checks.
    - [x] Verify README/package metadata rendering constraints.
    - [x] Verify GitHub Actions, Ruff Action, Pyright, ty, pytest, Vale, Renovate, and dependency policy references are current.
- [x] Task: Conductor - User Manual Verification 'Documentation And Packaging Evidence' (Protocol in workflow.md)

## Phase 3: Validation And Evidence

- [x] Task: Run baseline-safe quality gates.
    - [x] Run `uv lock --check`.
    - [x] Run release-readiness tests/checks.
    - [x] Run full pytest.
    - [x] Run Ruff check and format check.
    - [x] Run Pyright and ty.
    - [x] Run Vale for changed docs.
    - [x] Run Conductor swarm smoke checks.
- [x] Task: Record implementation evidence.
    - [x] Add `verification.md` with package/docs checks, remaining external gates, and CI evidence.
    - [ ] Add `review.md` after conductor review and fix loop.
    - [ ] Commit, push, and confirm GitHub Actions quality passes.
- [x] Task: Conductor - User Manual Verification 'Validation And Evidence' (Protocol in workflow.md)
