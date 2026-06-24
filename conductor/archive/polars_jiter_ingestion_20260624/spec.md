# Polars Jiter Ingestion Specification

## Overview

Add maintained ingestion helpers for local provider fixtures and exports. The implementation must use Polars lazy readers for tabular/JSONL paths and Jiter for JSON payload parsing, then emit normalized `Work` records from the schema layer. The legacy `pybibx/base` pandas-heavy runtime must remain untouched.

## Functional Requirements

- Add an ingestion package outside `pybibx/base`.
- Parse JSON provider payloads with Jiter and normalize them into `Work` records.
- Parse CSV/tabular exports with Polars lazy frames and normalize them into `Work` records.
- Support fixture-backed normalization for OpenAlex, Crossref, PubMed/MEDLINE, Semantic Scholar, ROR, ORCID, Unpaywall, arXiv, bioRxiv, medRxiv, Scopus, Web of Science, and Google Scholar BibTeX export.
- Preserve provider, input, schema, and library version metadata on normalized records.
- Keep live API calls, pagination, retries, bulk downloads, and provider credentials out of scope.

## Non-Functional Requirements

- Pass strict Ruff, Pyright, ty, pytest, and Conductor smoke checks.
- Keep fixtures small and deterministic.
- Avoid adding or modifying legacy pandas-based runtime files.

## Acceptance Criteria

- Tests confirm JSON fixtures parse through Jiter-backed helpers.
- Tests confirm CSV/tabular fixtures parse through Polars lazy helpers.
- Tests confirm normalized `Work` records include provider compatibility metadata.
- Tests confirm unsupported provider/format combinations fail closed.
