# Provider Ontology Foundation Plan

## Phase 1: Repository And Tooling Foundation

- [x] Task: Configure agent orchestration policy.
    - [x] Document Codex `gpt-5.5` as orchestrator, reviewer, verifier, and committer.
    - [x] Document Cline `deepseek-v4-flash` as an external worker lane gated by local provider configuration.
    - [x] Document the available multi-agent tool as the Codex swarm fallback.
    - [x] Define file ownership, isolated worktree, no-revert, and integration rules for delegated work.
    - [x] Add a blocker-first repo-local swarm launcher with dry-run defaults and fail-closed Cline gating.
- [ ] Task: Add modern packaging and environment plan.
    - [ ] Document Pixi environment expectations.
    - [ ] Document uv workspace/package layout.
    - [ ] Document latest-stable-CPython-only target.
    - [ ] Document optional extras for AI, RAG, graph, PDF, dashboard, and licensed-provider features.
- [ ] Task: Add strict quality tooling plan.
    - [ ] Plan Ruff strict lint/format rules.
    - [ ] Plan Pyright and ty strict type checks.
    - [ ] Plan pytest, coverage, and pytest-gremlins gates.
    - [ ] Plan Vale prose linting and Scalene profiling gates.
    - [ ] Plan Renovate, Ruff Action, TestSprite, and source-confirmed Una handling.
- [ ] Task: Conductor - User Manual Verification 'Repository And Tooling Foundation' (Protocol in workflow.md)

## Phase 2: Schema, Settings, And Versioning

- [ ] Task: Define the Pydantic v2 schema architecture.
    - [ ] Model provider payloads, normalized works, authors, institutions, citations, evidence sets, reports, and exports.
    - [ ] Add aliases and validators for OpenAlex, Schema.org, CSL-JSON, ROR, ORCID, DOI, PMID, and provider-specific fields.
    - [ ] Add JSON Schema snapshot expectations.
- [ ] Task: Define settings and version metadata.
    - [ ] Plan `pydantic-settings` config for provider credentials and rate limits.
    - [ ] Plan settings for Ollama, mistral.rs, hosted LLMs, LanceDB, Logfire, and local storage.
    - [ ] Add input, output, schema, provider, ontology, and library version fields.
- [ ] Task: Evaluate Jiter parser boundaries.
    - [ ] Use Jiter for fast iterable or partial JSON parsing where it beats standard paths.
    - [ ] Keep Polars streaming as the default bulk JSONL/tabular ingestion path.
- [ ] Task: Conductor - User Manual Verification 'Schema, Settings, And Versioning' (Protocol in workflow.md)

## Phase 3: Provider And Ontology Foundation

- [ ] Task: Define provider adapter groups.
    - [ ] Add open providers: OpenAlex, Crossref, PubMed/MEDLINE, OpenCitations, Semantic Scholar, ROR, ORCID, Unpaywall, arXiv, bioRxiv, medRxiv.
    - [ ] Add licensed providers: Scopus, Web of Science, Embase, EBSCO, ProQuest/Ovid, Cochrane/CINAHL/PsycINFO/ERIC/SSRN/PAIS/HeinOnline where access permits.
    - [ ] Add manual/import providers: Google Scholar BibTeX/RIS exports and legacy user files.
- [ ] Task: Define additive ontology model.
    - [ ] Map OpenAlex/Schema.org structural fields.
    - [ ] Add SPAR overlays: CiTO, FaBiO, FRAPO, PSO, ORG/ROR, ORCID.
    - [ ] Define semantic citation edge types, citation context text, and evidence IDs.
    - [ ] Add CSL-JSON, BibTeX, RIS, and Obsidian/BibLib-style Markdown interchange.
- [ ] Task: Conductor - User Manual Verification 'Provider And Ontology Foundation' (Protocol in workflow.md)

## Phase 4: Processing, Graphs, And Data Quality

- [ ] Task: Define Polars-first ingestion.
    - [ ] Plan lazy/streaming adapters for CSV, BibTeX/RIS-derived tables, JSON, JSONL, and snapshots.
    - [ ] Plan pandas compatibility only at legacy API boundaries.
    - [ ] Plan fixture datasets and benchmark slices.
- [ ] Task: Define graph computation stack.
    - [ ] Use RustWorkX for semantic citation and collaboration graph computation.
    - [ ] Preserve NetworkX export/compatibility.
    - [ ] Evaluate Graphina, PyBiblioNet, and PyG in later tracks.
- [ ] Task: Define data quality and pipeline layers.
    - [ ] Plan Kedro pipelines for ingestion and processing DAGs.
    - [ ] Plan Great Expectations suites for provider and schema validation.
    - [ ] Plan Deepchecks for data/model drift and quality checks.
- [ ] Task: Conductor - User Manual Verification 'Processing, Graphs, And Data Quality' (Protocol in workflow.md)

## Phase 5: AI, RAG, And Local Execution

- [ ] Task: Define structured AI stack.
    - [ ] Use PydanticAI as the primary typed-agent framework.
    - [ ] Use Instructor for simple LLM-to-Pydantic extraction, retries, and streaming partial outputs.
    - [ ] Use DSPy for prompt/program optimization.
    - [ ] Use LlamaIndex for optional RAG orchestration.
- [ ] Task: Define local/offline execution.
    - [ ] Support Ollama endpoints.
    - [ ] Support mistral.rs endpoints for OpenAI/Anthropic-compatible local serving, embeddings, multimodal paths, and metrics.
    - [ ] Evaluate optional Rig bridge for Rust agent orchestration.
    - [ ] Evaluate optional Monty code-mode sandbox with strict denial tests.
- [ ] Task: Define agent execution lanes for implementation.
    - [ ] Use Codex `gpt-5.5` as orchestrator for schema, provenance, integration, and final verification.
    - [ ] Use Cline `deepseek-v4-flash` only as a provider-verified external worker lane with isolated worktrees or disjoint file ownership.
    - [ ] Require Conductor-reviewed evidence before marking any external/manual lane task complete.
    - [ ] Use Codex swarm sub-agents for independent review or verification when Cline/DeepSeek is unavailable.
- [ ] Task: Define full-text RAG.
    - [ ] Route legal PDFs through Unpaywall and open preprint sources.
    - [ ] Evaluate Docling and PDFMux for structured PDF extraction.
    - [ ] Use FastEmbed and LanceDB for local embeddings and vector storage.
    - [ ] Require evidence-backed claims for report generation.
- [ ] Task: Conductor - User Manual Verification 'AI, RAG, And Local Execution' (Protocol in workflow.md)

## Phase 6: Observability, UI, And Reporting

- [ ] Task: Define observability.
    - [ ] Use Loguru for local structured logs.
    - [ ] Use Logfire and OpenTelemetry for traces, metrics, Pydantic validation analytics, agent/eval monitoring, and optional external backends.
    - [ ] Wire Prometheus metrics when mistral.rs is enabled.
    - [ ] Verify the exact Mantra package/source before pinning.
- [ ] Task: Define API, UI, and report surfaces.
    - [ ] Plan FastAPI/Pydantic service APIs.
    - [ ] Evaluate Reflex and Cosmograph for dashboards and GPU-style time-travel graph exploration.
    - [ ] Preserve legacy Flask compatibility during migration.
    - [ ] Plan PapersFlow-style citation-safe report workflows and BGBH/Country geospatial benchmarks.
- [ ] Task: Conductor - User Manual Verification 'Observability, UI, And Reporting' (Protocol in workflow.md)

## Phase 7: Verification And Iteration

- [ ] Task: Run Conductor artifact verification.
    - [ ] Verify core Conductor files are present and linked.
    - [ ] Verify MoSCoW requirements sections exist.
    - [ ] Verify design Mermaid fences exist for all major flows.
    - [ ] Verify every task and subtask in this plan uses `[ ]` markers.
- [ ] Task: Iterate plan review at least three times.
    - [ ] Pass 1: check every user-requested library/provider/ontology is represented.
    - [ ] Pass 2: check current-state versus target-state separation.
    - [ ] Pass 3: check implementation readiness, testability, and external-gate boundaries.
- [ ] Task: Conductor - User Manual Verification 'Verification And Iteration' (Protocol in workflow.md)
