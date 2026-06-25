# Workflow

## Task Workflow

- Work from one Conductor track at a time unless the user explicitly asks for a parallel track wave.
- Keep changes scoped to the active track.
- Commit after each completed task or checkpoint when implementation work begins.
- Record concise task summaries with Git notes or equivalent Conductor evidence.

## Agent Swarm Orchestration

- Codex with `gpt-5.5` is the primary orchestrator, integrator, and reviewer for Conductor track work.
- Cline with `deepseek-v4-flash` is an external worker lane when the local Cline provider is configured and available.
- The in-session multi-agent tool is the fallback swarm lane for Codex sub-agents when a local Cline/DeepSeek run is unavailable or should not touch the worktree.
- In this checkout, Cline/DeepSeek is considered blocked until `cline --json config` verifies `deepseek` with `deepseek-v4-flash`; use Codex sub-agents as the parallel worker fallback.
- Every worker must receive a bounded track phase, explicit file ownership, and a no-revert instruction.
- Parallel workers must use disjoint write scopes or isolated worktrees.
- External/manual worker output must be copied or summarized into Conductor evidence and reviewed by the Codex orchestrator before any task is marked complete.
- The orchestrator owns final integration, conflict resolution, verification, and commits.
- If a requested model/backend is unavailable, document the blocker and run the task with the next available lane only after preserving the intended assignment.

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
