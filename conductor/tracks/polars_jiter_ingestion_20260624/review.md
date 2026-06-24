# Polars Jiter Ingestion Review

Reviewed at `2026-06-24T03:20:11Z`.

## Review Lanes

- Orchestrator: Codex integrated parser fixes, updated Conductor evidence, and owns final commit, push, CI watch, and archive.
- Deputy: Codex subagent `019ef79e-2451-7610-b090-0a1675ca2e8b` reviewed archive readiness and found stale verification evidence, missing review evidence, thin phase checkpoint evidence, missing CI evidence, and active registry state.
- Implementation coverage: Codex subagent `019ef79e-4f5e-75e0-8a87-5a160e11c8a1` reviewed Jiter, Polars lazy parsing, compatibility metadata, fail-closed behavior, and provider fixture coverage.
- Parser contract quality: Codex subagent `019ef79e-75ac-7c13-9b8b-914ce70bb3f0` reviewed JSON/JSONL mechanics, fixture normalization paths, input-format inference, BibTeX parsing, RIS claims, and metadata propagation.

## Findings And Fixes

- Fixed missing JSONL ingestion: added `scan_jsonl` using Polars lazy `scan_ndjson`, normalized JSONL rows into `Work` records, exported the helper, and covered OpenAlex JSONL ingestion.
- Fixed RIS drift: added `.ris` inference and minimal RIS tagged-record normalization for credential-gated export files.
- Fixed BibTeX truncation: replaced the single flat-field parser with entry tokenization and one `Work` per BibTeX entry, including multiline fields.
- Fixed provider-blind `.txt` inference: `.txt` now infers TSV only for Web of Science-shaped tabular exports; other text files fail closed.
- Fixed weak test proof: tests now spy on `jiter.from_json`, assert compatibility metadata across JSON/CSV/TSV/BibTeX outputs, cover RIS, and cover unsupported text inference.
- Fixed missing review evidence by adding this review file and linking it from `index.md`.
- Fixed stale and thin verification evidence by refreshing `verification.md` with explicit per-phase checkpoints and current local validation.
- Active registry state is intentionally left for the archive commit after this verification commit passes GitHub Actions.

## Result

The Polars/Jiter ingestion track is implemented, reviewed, and ready for a verification commit. After that commit passes GitHub Actions, archive the track by moving it to `conductor/archive/polars_jiter_ingestion_20260624` and removing the active `conductor/tracks.md` entry.
