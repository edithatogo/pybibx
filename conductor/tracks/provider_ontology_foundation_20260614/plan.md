# Provider Ontology Foundation Plan

## Phase 1: Repository And Tooling Foundation

- [x] Task: Configure agent orchestration policy.
    - [x] Document Codex `gpt-5.5` as orchestrator, reviewer, verifier, and committer.
    - [x] Document Cline `deepseek-v4-flash` as an external worker lane gated by local provider configuration.
    - [x] Document the available multi-agent tool as the Codex swarm fallback.
    - [x] Define file ownership, isolated worktree, no-revert, and integration rules for delegated work.
    - [x] Add a blocker-first repo-local swarm launcher with dry-run defaults and fail-closed Cline gating.
- [x] Task: Add modern packaging and environment plan.
    - [x] Document Pixi environment expectations.
    - [x] Document uv workspace/package layout.
    - [x] Document latest-stable-CPython-only target.
    - [x] Document optional extras for AI, RAG, graph, PDF, dashboard, and licensed-provider features.
- [x] Task: Add strict quality tooling plan.
    - [x] Plan Ruff strict lint/format rules.
    - [x] Plan Pyright and ty strict type checks.
    - [x] Plan pytest, coverage, and pytest-gremlins gates.
    - [x] Plan Vale prose linting and Scalene profiling gates.
    - [x] Plan Renovate, Ruff Action, TestSprite, and source-confirmed Una handling.
- [x] Task: Conductor - User Manual Verification 'Repository And Tooling Foundation' (Protocol in workflow.md)

## Phase 2: Schema, Settings, And Versioning

- [x] Task: Define the Pydantic v2 schema architecture.
    - [x] Model provider payloads, normalized works, authors, institutions, citations, evidence sets, reports, and exports.
    - [x] Add aliases and validators for OpenAlex, Schema.org, CSL-JSON, ROR, ORCID, DOI, PMID, and provider-specific fields.
    - [x] Add JSON Schema snapshot expectations.
- [x] Task: Define settings and version metadata.
    - [x] Plan `pydantic-settings` config for provider credentials and rate limits.
    - [x] Plan settings for Ollama, mistral.rs, hosted LLMs, LanceDB, Logfire, and local storage.
    - [x] Add input, output, schema, provider, ontology, and library version fields.
- [x] Task: Evaluate Jiter parser boundaries.
    - [x] Use Jiter for fast iterable or partial JSON parsing where it beats standard paths.
    - [x] Keep Polars streaming as the default bulk JSONL/tabular ingestion path.
- [x] Task: Conductor - User Manual Verification 'Schema, Settings, And Versioning' (Protocol in workflow.md)

## Phase 3: Provider And Ontology Foundation

- [x] Task: Define provider adapter groups.
    - [x] Add open providers: OpenAlex, Crossref, PubMed/MEDLINE, OpenCitations, Semantic Scholar, ROR, ORCID, Unpaywall, arXiv, bioRxiv, medRxiv.
    - [x] Add licensed providers: Scopus, Web of Science, Embase, EBSCO, ProQuest/Ovid, Cochrane/CINAHL/PsycINFO/ERIC/SSRN/PAIS/HeinOnline where access permits.
    - [x] Add manual/import providers: Google Scholar BibTeX/RIS exports and legacy user files.
- [x] Task: Define additive ontology model.
    - [x] Map OpenAlex/Schema.org structural fields.
    - [x] Add SPAR overlays: CiTO, FaBiO, FRAPO, PSO, ORG/ROR, ORCID.
    - [x] Define semantic citation edge types, citation context text, and evidence IDs.
    - [x] Add CSL-JSON, BibTeX, RIS, and Obsidian/BibLib-style Markdown interchange.
- [x] Task: Conductor - User Manual Verification 'Provider And Ontology Foundation' (Protocol in workflow.md)

## Phase 4: Processing, Graphs, And Data Quality

- [x] Task: Define Polars-first ingestion.
    - [x] Plan lazy/streaming adapters for CSV, BibTeX/RIS-derived tables, JSON, JSONL, and snapshots.
    - [x] Plan pandas compatibility only at legacy API boundaries.
    - [x] Plan fixture datasets and benchmark slices.
- [x] Task: Define graph computation stack.
    - [x] Use RustWorkX for semantic citation and collaboration graph computation.
    - [x] Preserve NetworkX export/compatibility.
    - [x] Evaluate Graphina, PyBiblioNet, and PyG in later tracks.
- [x] Task: Define data quality and pipeline layers.
    - [x] Plan Kedro pipelines for ingestion and processing DAGs.
    - [x] Plan Great Expectations suites for provider and schema validation.
    - [x] Plan Deepchecks for data/model drift and quality checks.
- [x] Task: Conductor - User Manual Verification 'Processing, Graphs, And Data Quality' (Protocol in workflow.md)

## Phase 5: AI, RAG, And Local Execution

- [x] Task: Define structured AI stack.
    - [x] Use PydanticAI as the primary typed-agent framework.
    - [x] Use Instructor for simple LLM-to-Pydantic extraction, retries, and streaming partial outputs.
    - [x] Use DSPy for prompt/program optimization.
    - [x] Use LlamaIndex for optional RAG orchestration.
- [x] Task: Define local/offline execution.
    - [x] Support Ollama endpoints.
    - [x] Support mistral.rs endpoints for OpenAI/Anthropic-compatible local serving, embeddings, multimodal paths, and metrics.
    - [x] Evaluate optional Rig bridge for Rust agent orchestration.
    - [x] Evaluate optional Monty code-mode sandbox with strict denial tests.
- [x] Task: Define agent execution lanes for implementation.
    - [x] Use Codex `gpt-5.5` as orchestrator for schema, provenance, integration, and final verification.
    - [x] Use Cline `deepseek-v4-flash` only as a provider-verified external worker lane with isolated worktrees or disjoint file ownership.
    - [x] Require Conductor-reviewed evidence before marking any external/manual lane task complete.
    - [x] Use Codex swarm sub-agents for independent review or verification when Cline/DeepSeek is unavailable.
- [x] Task: Define full-text RAG.
    - [x] Route legal PDFs through Unpaywall and open preprint sources.
    - [x] Evaluate Docling and PDFMux for structured PDF extraction.
    - [x] Use FastEmbed and LanceDB for local embeddings and vector storage.
    - [x] Require evidence-backed claims for report generation.
- [x] Task: Conductor - User Manual Verification 'AI, RAG, And Local Execution' (Protocol in workflow.md)

## Phase 6: Observability, UI, And Reporting

- [x] Task: Define observability.
    - [x] Use Loguru for local structured logs.
    - [x] Use Logfire and OpenTelemetry for traces, metrics, Pydantic validation analytics, agent/eval monitoring, and optional external backends.
    - [x] Wire Prometheus metrics when mistral.rs is enabled.
    - [x] Verify the exact Mantra package/source before pinning.
- [x] Task: Define API, UI, and report surfaces.
    - [x] Plan FastAPI/Pydantic service APIs.
    - [x] Evaluate Reflex and Cosmograph for dashboards and GPU-style time-travel graph exploration.
    - [x] Preserve legacy Flask compatibility during migration.
    - [x] Plan PapersFlow-style citation-safe report workflows and BGBH/Country geospatial benchmarks.
- [x] Task: Conductor - User Manual Verification 'Observability, UI, And Reporting' (Protocol in workflow.md)

## Phase 7: Verification And Iteration

- [x] Task: Run Conductor artifact verification.
    - [x] Verify core Conductor files are present and linked.
    - [x] Verify MoSCoW requirements sections exist.
    - [x] Verify design Mermaid fences exist for all major flows.
    - [x] Verify every task and subtask in this plan uses `[ ]` markers.
- [x] Task: Iterate plan review at least three times.
    - [x] Pass 1: check every user-requested library/provider/ontology is represented.
    - [x] Pass 2: check current-state versus target-state separation.
    - [x] Pass 3: check implementation readiness, testability, and external-gate boundaries.
- [x] Task: Conductor - User Manual Verification 'Verification And Iteration' (Protocol in workflow.md)
