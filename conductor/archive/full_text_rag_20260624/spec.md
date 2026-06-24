# Spec

## Goals

- Route legal full text through Unpaywall open-access metadata and open preprint providers.
- Keep closed, credentialed, or non-open full-text sources out of local RAG by default.
- Represent Docling and PDFMux behind a common parser-evaluation contract.
- Represent FastEmbed embedding records and LanceDB vector-store records without making optional RAG dependencies mandatory for baseline imports.
- Build evidence-grounded extraction contracts that require claim support to map to concrete text chunks.

## Non-Goals

- No hosted PDF parsing, hosted LLM calls, or live provider downloads in this track.
- No mandatory installation of Docling, PDFMux, FastEmbed, LanceDB, Instructor, or LlamaIndex in the baseline dependency set.
- No replacement of legacy summarization or web-app AI flows in this track.

## Acceptance

- Unpaywall routes only open-access full-text URLs.
- arXiv, bioRxiv, and medRxiv fixtures can produce legal preprint PDF routes.
- Docling and PDFMux are evaluated through a single typed parser interface with local/credential/terms boundaries.
- Markdown-derived chunks preserve source locators and section context.
- Embedding and vector-store records stay aligned by chunk identifier.
- Evidence-grounded extractions fail closed when supporting chunks are absent.
- Full local quality and type gates pass.

