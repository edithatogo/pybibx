# Provider Registry Fixtures Specification

## Overview

Add a provider registry and local fixture manifest for the next ingestion track. The registry must cover open APIs, export/import-only sources, and credential/license-gated sources without implementing live network clients or scraping.

## Functional Requirements

- Register OpenAlex, Crossref, PubMed, MEDLINE, OpenCitations, Semantic Scholar, ROR, ORCID, Unpaywall, arXiv, bioRxiv, medRxiv, Google Scholar export import, Scopus, and Web of Science.
- Mark Scopus and Web of Science as credential/license-gated connectors.
- Mark Google Scholar as export/import-only and explicitly non-scraping.
- Register preprint sources for arXiv, bioRxiv, and medRxiv.
- Record provider capabilities, access modes, base URLs, docs URLs, supported input/output formats, endpoints, fixture paths, provider version stamps, and terms notes.
- Add local static fixtures for each registered provider.
- Integrate the registered provider set with default settings.

## Non-Functional Requirements

- Keep live HTTP clients, provider adapters, and Polars ingestion out of scope.
- Keep fixtures small and safe for repository storage.
- Pass baseline Ruff, Pyright, ty, pytest, and Conductor smoke checks.

## Acceptance Criteria

- Tests confirm every requested provider is registered exactly once.
- Tests confirm Scopus/Web of Science are credential-gated and Google Scholar has no live endpoint.
- Tests confirm all fixture paths exist and JSON fixtures parse.
- Tests confirm provider registry and default settings agree.
