# Swarm Phase 3 Evidence: Provider And Ontology Foundation

Agent: `019ecba7-636b-71d0-b1d1-803af007a887`

## Findings

- Providers should be grouped as open, licensed/credential-gated, and manual/export-only.
- OpenAlex is the only provider with meaningful adapter-like code today.
- Current README documents Scopus, Web of Science, PubMed, and OpenAlex file/API workflows; Google Scholar must remain import-only.
- CSL-JSON, RIS, Markdown, and Parquet are target contracts, not existing behavior.

## Implementation Shape

- Build a provider registry with access mode, credential requirements, rate-limit policy, provenance, and version metadata.
- Wrap OpenAlex first with a Pydantic adapter while preserving JSON, CSV, ID normalization, reference preservation, and legacy column behavior.
- Add sibling adapters later for Crossref, PubMed/MEDLINE, OpenCitations, Semantic Scholar, ROR, ORCID, Unpaywall, and preprint sources.
- Keep licensed providers fail-closed without credentials.
- Model ontology overlays additively: OpenAlex/Schema.org base plus CiTO, FaBiO, FRAPO, PSO, ORG/ROR, ORCID, and CSL-JSON facets.

## Acceptance Criteria

- Every source routes to `open`, `licensed`, or `manual_export`.
- Provider adapters emit immutable raw audit payloads and validated normalized records.
- Google Scholar has no scraper path.
- Ontology facets do not replace normalized bibliographic fields.

## Blockers

- No provider registry/settings layer exists yet.
- OpenAlex reference expansion can call live APIs and needs deterministic fixtures and failure metadata.
- Interchange contracts are not implemented.

