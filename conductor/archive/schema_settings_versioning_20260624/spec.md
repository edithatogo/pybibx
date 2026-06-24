# Schema Settings Versioning Specification

## Overview

Add the first maintained PyBibX 6.0 data-contract layer without rewriting the legacy `pybibx/base` runtime. The layer must provide strict Pydantic v2 models, typed runtime settings, and explicit version profiles for library, schema, provider, input, and output compatibility.

## Functional Requirements

- Add Pydantic v2 models for works, authors, institutions, citations, ontology facets, evidence sets, and exports.
- Add ontology enums for provider names, source/input formats, output formats, citation intent, work type, publication status, and export profile.
- Add reusable version-profile models for library, schema, provider adapter, input, output, ontology, and settings metadata.
- Add typed `pydantic-settings` configuration for provider credentials, rate limits, local model endpoints, storage paths, observability, and feature gates.
- Expose JSON Schema snapshot helpers for maintained models.
- Keep all new code outside `pybibx/base` and preserve legacy import behavior.
- Make the new schema/settings modules part of baseline CI rather than an optional untested extra.

## Non-Functional Requirements

- Pass Ruff strict linting, Pyright strict mode, ty, and pytest on the maintained surface.
- Avoid hosted-service requirements or mandatory credentials.
- Do not add provider network clients, Polars ingestion, RustWorkX graphs, RAG, or AI agents in this track.

## Acceptance Criteria

- New schema and settings modules can be imported and instantiated in baseline CI.
- Models validate DOI, ORCID, ROR URL, date, citation-count, and evidence consistency constraints.
- Version metadata is attached to records and exports.
- Tests cover representative valid and invalid model/settings cases.
- Conductor verification records local checks and known boundaries.
