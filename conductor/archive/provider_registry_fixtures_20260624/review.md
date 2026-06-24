# Provider Registry Fixtures Review

Reviewed at `2026-06-24T03:07:46Z`.

## Review Lanes

- Orchestrator: Codex integrated the provider contract fixes, updated Conductor evidence, and owns final commit, push, CI watch, and archive.
- Deputy: Codex subagent `019ef793-a806-72b1-af4c-02dd5edf24d1` reviewed archive readiness and found stale verification evidence, missing review evidence, thin phase checkpoint evidence, and active registry state.
- Implementation coverage: Codex subagent `019ef793-d4c9-70a0-bfff-eabcec3ec94d` reviewed provider registration, settings parity, fixture existence, JSON parsing, and access-mode boundaries after the ORCID/settings fix and found no remaining blockers.
- Fixture and contract quality: Codex subagent `019ef794-007d-7b33-b405-bde5634e7f45` reviewed fixture formats, endpoint response metadata, and provider URLs.

## Findings And Fixes

- Fixed ORCID settings drift: ORCID remains an open provider with optional token configuration rather than a disabled credential-gated provider.
- Fixed settings parity coverage: tests now assert provider settings mirror registry credential flags and rate limits.
- Fixed Web of Science fixture format drift: added `InputFormat.TSV`, declared the Web of Science `.txt` fixture as TSV, and made ingestion infer `.txt`/`.tsv` as TSV.
- Fixed endpoint response-format ambiguity: `ProviderEndpoint` now has `response_format` for provider-native JSON/XML responses, while `supported_output_formats` remains the normalized PyBibX export surface.
- Fixed OpenCitations API metadata: registry now uses `https://api.opencitations.net/index/v2`.
- Fixed missing review evidence by adding this review file and linking it from `index.md`.
- Fixed thin checkpoint evidence by refreshing `verification.md` with explicit per-phase checkpoints.
- Fixed active registry state by moving the track to `conductor/archive/provider_registry_fixtures_20260624` after the verification commit passed GitHub Actions and removing the active `conductor/tracks.md` entry.

## Result

The provider registry fixtures track is implemented, reviewed, CI-verified, and archived.
