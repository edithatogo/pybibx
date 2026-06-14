# Workflow

## Task Workflow

- Work from one Conductor track at a time unless the user explicitly asks for a parallel track wave.
- Keep changes scoped to the active track.
- Commit after each completed task or checkpoint when implementation work begins.
- Record concise task summaries with Git notes or equivalent Conductor evidence.

## Quality Gates

- Target 90% test coverage for new 6.0 code, with ratcheted baselines for legacy code.
- Require Ruff format/check, Pyright, ty, pytest, and relevant schema snapshot checks before completing implementation tasks.
- Use Vale for prose docs and Scalene for performance-sensitive ingestion/graph work.
- For external services, separate local verification from credential-gated verification.

## Phase Completion Verification and Checkpointing Protocol

Each phase plan must end with a manual verification checkpoint:

- Confirm all expected files, settings, tests, or docs for the phase exist.
- Confirm no unrelated files were modified.
- Confirm the phase acceptance criteria are met.
- Record blockers separately from completed local work.

