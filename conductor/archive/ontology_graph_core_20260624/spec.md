# Spec

## Goals

- Add strict Pydantic v2 models for additive CiTO, FaBiO, FRAPO, PSO, ORG, ROR, ORCID, and CSL ontology facets.
- Use RustWorkX as the maintained graph backend for citation and co-authorship builders.
- Preserve NetworkX compatibility through explicit export helpers.
- Keep graph builders independent from the legacy `pybibx.base` runtime.

## Non-Goals

- No replacement of legacy plotting, historiograph, or topic graph internals in this track.
- No live provider calls, RAG extraction, or LLM citation classification in this track.
- No GraphML or Cosmograph exporter implementation in this track.

## Acceptance

- Ontology models validate DOI, ORCID, and ROR identifiers.
- Citation graphs retain semantic CiTO edge intent, context, evidence identifiers, and weighted edge semantics.
- Co-authorship graphs aggregate repeated shared publications.
- NetworkX export preserves node and edge attributes.
- Quality, type, and Conductor checks pass.

