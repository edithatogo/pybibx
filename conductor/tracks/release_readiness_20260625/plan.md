# Release Readiness Plan

## Phase 1: Release Boundary And Tests

- [ ] Task: Define release-readiness assertions.
    - [ ] Add tests or checks for package metadata, wheel build, import smoke, and README/long-description health.
    - [ ] Add checks that baseline dependency policy still avoids all-extras on Python 3.14.
    - [ ] Add tests or scripts that fail closed if public API exports drift unexpectedly.
- [ ] Task: Define the 6.0 alpha surface.
    - [ ] Classify modules as public, provisional, optional, legacy, or internal.
    - [ ] Identify docs/examples that must exist before alpha.
    - [ ] Identify external blockers that must remain out of repo-local completion claims.
- [ ] Task: Conductor - User Manual Verification 'Release Boundary And Tests' (Protocol in workflow.md)

## Phase 2: Documentation And Packaging Evidence

- [ ] Task: Add release-readiness documentation.
    - [ ] Add migration notes from PyBibX 5.9.2 to maintained 6.0 modules.
    - [ ] Add optional-extra compatibility matrix.
    - [ ] Add release notes covering completed tracks, limitations, and blockers.
    - [ ] Add short examples for schema/settings, provider pipeline, legacy bridge, reports, and quality lanes where implemented.
- [ ] Task: Refresh packaging and CI evidence.
    - [ ] Run wheel build and import smoke checks.
    - [ ] Verify README/package metadata rendering constraints.
    - [ ] Verify GitHub Actions, Ruff Action, Pyright, ty, pytest, Vale, Renovate, and dependency policy references are current.
- [ ] Task: Conductor - User Manual Verification 'Documentation And Packaging Evidence' (Protocol in workflow.md)

## Phase 3: Validation And Evidence

- [ ] Task: Run baseline-safe quality gates.
    - [ ] Run `uv lock --check`.
    - [ ] Run release-readiness tests/checks.
    - [ ] Run full pytest.
    - [ ] Run Ruff check and format check.
    - [ ] Run Pyright and ty.
    - [ ] Run Vale for changed docs.
    - [ ] Run Conductor swarm smoke checks.
- [ ] Task: Record implementation evidence.
    - [ ] Add `verification.md` with package/docs checks, remaining external gates, and CI evidence.
    - [ ] Add `review.md` after conductor review and fix loop.
    - [ ] Commit, push, and confirm GitHub Actions quality passes.
- [ ] Task: Conductor - User Manual Verification 'Validation And Evidence' (Protocol in workflow.md)
