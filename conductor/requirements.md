# Requirements

## Must

- Define a track orchestration policy that assigns Codex `gpt-5.5` as orchestrator/reviewer, Cline `deepseek-v4-flash` as an external worker lane when locally configured, and the available multi-agent tool as the fallback swarm mechanism.
- Define Pydantic v2 schema contracts for provider payloads, normalized works, authors, institutions, citations, ontology facets, evidence sets, reports, and exports.
- Version all inputs, outputs, schema profiles, ontology profiles, provider adapters, and library compatibility metadata.
- Add typed configuration with `pydantic-settings` for provider credentials, API rate limits, local model endpoints, storage paths, observability, and feature gates.
- Plan Polars lazy/streaming ingestion for large provider files and API payloads, with pandas confined to legacy compatibility boundaries.
- Include providers for OpenAlex, Crossref, PubMed/MEDLINE, OpenCitations, Semantic Scholar, ROR, ORCID, Unpaywall, arXiv, bioRxiv, medRxiv, Scopus, Web of Science, and Google Scholar export import.
- Treat Scopus, Web of Science, Embase, EBSCO, ProQuest/Ovid, and similar sources as credential/license-gated connectors.
- Adopt SPAR-style additive ontology overlays, including CiTO, FaBiO, FRAPO, PSO, ORG/ROR, ORCID, OpenAlex/Schema.org, and CSL-JSON.
- Preserve legal full-text boundaries using Unpaywall/preprints and provider terms.
- Make AI-generated reports citation-safe: every synthesized claim must map to verified evidence.
- Add Conductor design diagrams and track plans with unchecked task markers for implementation follow-through.

## Should

- Run parallel track work only with explicit file ownership, isolated worktrees or disjoint write scopes, and orchestrator-owned integration.
- Use RustWorkX as the main graph computation backend, with NetworkX compatibility/export.
- Evaluate Jiter for fast iterable/partial JSON parsing where it improves provider or streaming-agent performance.
- Use PydanticAI as the primary typed-agent framework and Instructor as the simple LLM-to-Pydantic extraction adapter.
- Use DSPy for prompt/program optimization and LlamaIndex for optional RAG orchestration.
- Support Ollama and mistral.rs for local model execution; prefer mistral.rs where Rust-native, multimodal, OpenAI/Anthropic-compatible serving and metrics matter.
- Use FastEmbed and LanceDB for local embeddings and vector storage.
- Evaluate Docling and PDFMux for full-text scientific PDF parsing.
- Add Loguru, Logfire, OpenTelemetry, and optional Prometheus integrations for observability.
- Plan Kedro pipelines, Great Expectations validation suites, and Deepchecks checks for data/model quality.
- Add CI/tooling for Pixi, uv workspaces, Ruff Action, Pyright, ty, pytest, pytest-gremlins, Scalene, Vale, Renovate, and TestSprite.
- Use BGBH/Country as a reference benchmark for geospatial country-collaboration visualization.

## Could

- Add a Rust workspace for optional Rig/mistral.rs bridge services.
- Evaluate Graphina, PyBiblioNet, PyG, Reflex, Cosmograph, and Monty in later tracks.
- Add Obsidian/BibLib-style Markdown note export/import for plain-text bibliography workflows.
- Add PapersFlow-style citation-safe report generation workflows and Ryzome-style context-library exports.
- Add provider-specific benchmark datasets from OpenAlex snapshots, OpenCitations, Open Bibliometrics, and curated fixture packs.

## Won't

- Won't scrape Google Scholar by default.
- Won't make paid providers, hosted PDF parsing, hosted LLMs, Rig, Ryzome, Reflex, Cosmograph, Monty, or cloud observability mandatory for core library use.
- Won't remove legacy compatibility before public adapters, migration notes, and tests exist.
- Won't let AI systems invent sources, citations, methods, or unsupported claims.
- Won't pin ambiguous dependencies such as Una or Mantra until exact packages and project fit are verified.
