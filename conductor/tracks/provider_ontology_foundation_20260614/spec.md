# Provider Ontology Foundation Specification

## Goal

Define the first PyBibX 6.0 foundation track: a strict, versioned, provider-aware, ontology-backed architecture that can be implemented incrementally without breaking current PyBibX 5.9.2 workflows.

## Outcomes

- Current PyBibX capabilities remain documented as the baseline.
- Future implementation has a clear schema, provider, ontology, tooling, observability, and AI/RAG roadmap.
- Open providers, paid providers, manual import paths, and local execution modes are explicitly separated.
- AI and agentic features are constrained by Pydantic validation, source provenance, and evidence-backed outputs.

## Public Interface Plan

- Add versioned schema models for works, authors, institutions, citations, providers, evidence sets, reports, exports, and ontology facets.
- Add typed settings for provider credentials, local runtime endpoints, feature gates, paths, and observability.
- Add provider adapter interfaces that normalize raw inputs into Pydantic models and Polars frames.
- Add export contracts for CSL-JSON, BibTeX, RIS, Markdown notes, Parquet, and compatibility dataframes.
- Keep legacy `pbx_probe` behavior behind adapters until migration tests prove parity.

## Constraints

- Google Scholar support is import-only.
- Licensed providers require credentials and must not be hard dependencies.
- Local/air-gapped operation must be possible for core ingestion, graph, and schema workflows.
- AI workflows cannot emit accepted claims without evidence IDs and source provenance.
- Ambiguous tools such as Una and Mantra must be verified before pinning.

## Acceptance Criteria

- The Conductor requirements and design files cover all requested libraries, providers, ontologies, RAG/local execution components, and quality gates.
- The Conductor workflow documents how Codex `gpt-5.5`, Cline `deepseek-v4-flash`, and available swarm-style sub-agents are assigned to track phases.
- Track tasks are complete enough for a future `/conductor:implement` pass to start without re-planning the foundation.
- The plan separates current state from target state and local implementation from external/manual gates.
