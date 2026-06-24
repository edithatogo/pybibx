# Specification

## Overview

Add the first maintained UI/reporting foundation for PyBibX 6.0 without rewriting the legacy Flask app or introducing mandatory frontend dependencies.

## Functional Requirements

- Add typed report models for citation-safe, PapersFlow-style outputs where each synthesized claim declares supporting evidence sets.
- Add deterministic CSL-JSON export from normalized `Work` records.
- Add BibLib/Obsidian-style Markdown note bundle export from normalized `Work` records.
- Add optional Reflex dashboard and Cosmograph graph-export plan specs.
- Add settings and packaging lanes for UI/report features while keeping heavy UI dependencies optional.
- Document the UI/report generation flow in Conductor design materials.

## Non-Functional Requirements

- Report claims must fail closed when evidence references are absent or unknown.
- Optional UI/report dependencies must not be required to import `pybibx.reports`.
- Markdown and CSL exports must be deterministic for fixture-backed tests.
- Legacy `pybibx/base` UI behavior remains untouched.

## Out of Scope

- Building a live Reflex application.
- Rendering Cosmograph in a browser.
- Calling PapersFlow or any hosted report API.
- Implementing full BibTeX/RIS serialization beyond exposing the planned output formats.

## Acceptance Criteria

- `pybibx.reports` imports without optional UI dependencies installed.
- Citation-safe report construction validates claims, evidence sets, citations, sections, and manifest counts.
- Markdown rendering includes evidence locators.
- CSL-JSON and BibLib-style Markdown exports are covered by tests.
- Packaging metadata exposes optional `reports` and `ui` extras.
- Local quality and type gates pass.
