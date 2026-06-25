# End-To-End Provider Pipeline Specification

## Overview

Build the first user-visible PyBibX 6.0 provider pipeline that turns real provider inputs into versioned normalized records without falling back to the legacy pandas-heavy runtime. This track should connect the existing provider registry, fixtures, Polars/Jiter ingestion, schema validation, settings, and export contracts into a coherent headless workflow.

## Functional Requirements

- Add a provider pipeline entry point that accepts configured provider names, local fixture/input paths, and output format choices.
- Support at least OpenAlex, Crossref, and PubMed/MEDLINE through the existing open-provider registry and fixtures.
- Route raw provider payloads through immutable raw-record audit metadata, Polars/Jiter parsing, Pydantic validation, and normalized `Work` records.
- Attach library, schema, provider, input, and output version metadata to pipeline results and exports.
- Produce baseline exports for JSONL and CSL-JSON; include Parquet only if it is already supported without making optional heavy dependencies mandatory.
- Keep credential-gated and export-only providers explicit: Scopus/Web of Science remain disabled unless credentials are configured, and Google Scholar remains import/export-only.
- Provide CLI or Python API examples that run offline against fixtures.

## Non-Functional Requirements

- Must remain baseline-safe on Python 3.14 using `uv sync --group dev`, not `uv sync --all-extras`.
- Must avoid network calls in baseline tests.
- Must keep pandas confined to legacy compatibility modules.
- Must preserve strict Ruff, Pyright, ty, and pytest gates.
- Must record provider terms/access boundaries in code or docs where a provider lane is exposed.

## Acceptance Criteria

- A developer can run an offline command or API call that ingests OpenAlex, Crossref, and PubMed/MEDLINE fixtures and returns normalized `Work` records.
- Pipeline outputs include explicit compatibility/version profiles.
- JSONL and CSL-JSON exports are tested with deterministic fixture data.
- Tests cover success paths, invalid provider names, unsupported provider access modes, schema failures, and missing input files.
- Conductor verification records local checks, no-network boundaries, and any remaining provider limitations.

## Out Of Scope

- Live API clients and credentialed provider downloads.
- Full-text RAG, graph building, UI dashboards, and report generation.
- Removing or rewriting legacy `pybibx/base` behavior.
