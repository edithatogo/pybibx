# Review

Review completed on 2026-06-24 using Codex subagents after the Cline lane remained blocked by non-TTY configuration.

## Findings Fixed

- `pybibx.reports` optional import coverage was too weak because tests imported reports before checking the dependency boundary. The import test now runs in a subprocess with Reflex, Cosmograph, legacy UI, and heavy scientific dependencies blocked.
- Report claim and section references allowed blank or duplicate identifiers through public constructors. Claims and sections now require non-empty unique references.
- Citation-safe reports did not reject duplicate works, citations, evidence sets, or claims. Report validation now fails closed on duplicate IDs.
- Citation evidence item IDs were not validated against report evidence items. Citation evidence chains now fail closed when they reference absent evidence items.
- Manually constructed report manifests could disagree with report evidence-set IDs. Report validation now checks manifest evidence IDs against report evidence sets.
- BibLib Markdown exports used a CSL bibliography manifest profile. BibLib exports now use the BibLib Markdown profile and Markdown output format.
- BibLib Markdown note filenames could collide after safe-name normalization and silently drop records. Note bundle export now rejects filename collisions.
- Closeout evidence was incomplete. This review file, index link, acceptance trace, refreshed verification evidence, and archive flow were added.

## Acceptance Trace

| Criterion | Evidence |
| --- | --- |
| `pybibx.reports` imports without optional UI dependencies installed. | `test_reports_package_imports_without_optional_ui_dependencies` blocks Reflex, Cosmograph, legacy UI, and heavy scientific imports in a subprocess. |
| Citation-safe report construction validates claims, evidence sets, citations, sections, and manifest counts. | `test_report_claims_fail_closed_without_evidence_ids` and `test_citation_safe_report_validates_claim_evidence_and_citations`. |
| Markdown rendering includes evidence locators. | `test_papersflow_style_markdown_renders_claims_with_evidence_references`. |
| CSL-JSON and BibLib-style Markdown exports are covered by tests. | `test_csl_json_and_biblib_markdown_exports_are_deterministic`. |
| Packaging metadata exposes optional `reports` and `ui` extras. | `test_dependency_groups_separate_legacy_and_modern_stacks`. |
| Local quality and type gates pass. | See `verification.md`. |

## Manual Checkpoint

- Expected files/settings/tests/docs were reviewed and updated for the UI/Reports track.
- No unrelated files were intentionally changed.
- Acceptance criteria are mapped above and validated locally.
- Remaining blocker is external only until GitHub Actions has passed on the pushed closeout commit.
