# Agent Orchestration

## Purpose

This file defines how PyBibX Conductor tracks should be orchestrated across Codex, Cline, and available swarm-style sub-agents.

## Available Local Runners

- Cline CLI is available at `/opt/homebrew/bin/cline`.
- Codex CLI is available at `/Applications/Codex.app/Contents/Resources/codex`.
- A local `swarm` skill file was not found in the available skill directories.
- The current session exposes multi-agent sub-agents, including `gpt-5.5`, through the in-session multi-agent tool.
- Cline/DeepSeek availability means the CLI and provider/model are usable for the specific checkout; CLI presence alone is not enough to mark that lane verified.

## Lanes

### Codex Orchestrator Lane

- Runner: Codex.
- Model: `gpt-5.5`.
- Role: primary orchestrator, integrator, reviewer, verifier, and committer.
- Ownership: Conductor registry, track status, integration patches, final checks, commits, and handoff notes.
- Example:

```bash
/Applications/Codex.app/Contents/Resources/codex exec \
  -C /Volumes/PortableSSD/GitHub/pybibx \
  -m gpt-5.5 \
  --sandbox workspace-write \
  --ask-for-approval never \
  "Implement the next bounded task from conductor/tracks/provider_ontology_foundation_20260614/plan.md. Preserve unrelated changes."
```

### Cline Worker Lane

- Runner: Cline.
- Model: `deepseek-v4-flash`.
- Role: external worker for bounded, disjoint track phases when the provider is configured locally.
- Ownership: only the files explicitly assigned in the prompt or the isolated worktree created by Cline.
- Gate: run this lane only after confirming the Cline provider/model configuration outside logs that may expose secrets.
- Example:

```bash
cline \
  --cwd /Volumes/PortableSSD/GitHub/pybibx \
  --worktree \
  --provider deepseek \
  --model deepseek-v4-flash \
  --thinking medium \
  "Work only on the assigned Conductor phase. Do not revert others' edits. Report changed files and verification."
```

If the `deepseek-v4-flash` provider/model is not configured, record the blocker in the active track and use the Codex swarm fallback for local progress.

### Codex Swarm Fallback Lane

- Runner: in-session multi-agent tool.
- Model: `gpt-5.5` when explicitly requested.
- Role: parallel exploration, verification, or bounded implementation in disjoint write scopes.
- Gate: use only when the user explicitly asks for sub-agents, delegation, parallel agents, or swarm work.
- Close sub-agents after their outputs are integrated or rejected.

## Assignment Rules

- Use Codex `gpt-5.5` for architecture decisions, Pydantic schema boundaries, provider provenance policy, integration, and final verification.
- Use Cline `deepseek-v4-flash` for isolated drafting, fixture generation, prose/doc passes, provider adapter scaffolds, and non-overlapping implementation slices.
- Use Codex sub-agents for independent reviews, codebase exploration, and verification that can run while the orchestrator continues.
- Do not let two agents edit the same file set concurrently.
- Every delegated task must include file ownership, acceptance criteria, and no-revert instructions.
- External/manual lane output must be copied or summarized into the active Conductor track as reviewed evidence before the corresponding task can be marked complete.

## Track Assignment Matrix

| Track Phase | Primary Lane | Secondary Lane | Notes |
| --- | --- | --- | --- |
| Repository and tooling foundation | Codex `gpt-5.5` | Cline `deepseek-v4-flash` | Codex owns final config; Cline can draft candidate files in an isolated worktree. |
| Schema, settings, and versioning | Codex `gpt-5.5` | Codex swarm | Keep schema decisions under orchestrator control. |
| Provider and ontology foundation | Codex `gpt-5.5` | Cline `deepseek-v4-flash` | Cline can scaffold provider fixtures/adapters with disjoint file ownership. |
| Processing, graphs, and data quality | Codex `gpt-5.5` | Cline `deepseek-v4-flash` | Use isolated worktrees for Polars/RustWorkX slices. |
| AI, RAG, and local execution | Codex `gpt-5.5` | Codex swarm | Security-sensitive boundaries remain under Codex review. |
| Observability, UI, and reporting | Codex `gpt-5.5` | Cline `deepseek-v4-flash` | Cline can draft docs/UI prototypes; Codex verifies. |
| Verification and iteration | Codex `gpt-5.5` | Codex swarm | Swarm agents can run independent checklist reviews. |

## Verification

- Verify `cline --help` and `codex --help` before documenting CLI usage.
- Reject completion wording that marks Cline/DeepSeek as available, verified, or complete unless a local provider/model check has been recorded for this checkout.
- Verify all worker outputs with the active track's quality gates.
- Run `git diff --check` before committing.
- Commit only from the orchestrator lane.
