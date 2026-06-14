# Design

## Provider Ingestion

```mermaid
flowchart LR
    UserInput[User files or API query] --> Router[Provider router]
    Router --> Open[Open providers]
    Router --> Licensed[Credential-gated providers]
    Router --> Manual[Manual/export-only providers]
    Open --> RawAudit[Raw immutable audit record]
    Licensed --> RawAudit
    Manual --> RawAudit
    RawAudit --> Parse[Polars streaming or Jiter JSON parser]
    Parse --> Validate[Pydantic schema gate]
    Validate --> Normalized[Versioned normalized records]
```

## Settings Resolution

```mermaid
flowchart TD
    Env[Environment variables] --> Settings[pydantic-settings]
    Files[Config files] --> Settings
    CLI[CLI/API overrides] --> Settings
    Settings --> Providers[Provider clients]
    Settings --> Runtime[Local or hosted model runtime]
    Settings --> Observability[Logfire/OTel/Loguru config]
    Settings --> Storage[Cache/vector/output paths]
```

## Versioned Schema Gate

```mermaid
flowchart LR
    Raw[Provider payload] --> Adapter[Provider adapter]
    Adapter --> Model[Pydantic v2 model]
    Model --> Schema[JSON Schema snapshot]
    Model --> Record[Normalized record]
    Record --> Metadata[provider_version + schema_version + library_version]
    Metadata --> Export[CSL/BibTeX/RIS/Markdown/Parquet]
```

## Additive Ontology Model

```mermaid
flowchart TD
    Work[OpenAlex/Schema.org Work] --> FaBiO[FaBiO document type]
    Work --> CiTO[CiTO citation intent]
    Work --> FRAPO[FRAPO funding]
    Work --> PSO[PSO publication status]
    Work --> ORG[ORG/ROR institution graph]
    Work --> ORCID[ORCID author identity]
    Work --> CSL[CSL-JSON interchange]
```

## Full-Text RAG

```mermaid
flowchart LR
    DOI[DOI or provider work] --> OA[Unpaywall/preprint legality check]
    OA --> PDF[Legal PDF or full text]
    PDF --> Parser[Docling/PDFMux evaluation]
    Parser --> Chunks[Section-aware chunks]
    Chunks --> Embeddings[FastEmbed or local runtime embeddings]
    Embeddings --> LanceDB[LanceDB evidence store]
    LanceDB --> Retriever[LlamaIndex/PydanticAI retriever]
    Retriever --> Claims[Citation-safe structured claims]
```

## Agentic Extraction

```mermaid
flowchart TD
    Task[Research task] --> Agent[PydanticAI agent]
    Agent --> Tools[Provider/search/RAG tools]
    Agent --> Instructor[Instructor extraction adapter]
    Agent --> DSPy[DSPy optimizer]
    Tools --> Evidence[Verified evidence set]
    Instructor --> Typed[Pydantic output]
    DSPy --> Typed
    Evidence --> Typed
    Typed --> Validate[Schema and provenance validation]
```

## Local Runtime And Rust Bridge

```mermaid
flowchart LR
    Settings[Runtime settings] --> Ollama[Ollama]
    Settings --> Mistral[mistral.rs]
    Settings --> Hosted[Hosted provider]
    Mistral --> Prom[Prometheus metrics]
    Mistral --> Rig[Optional Rig bridge]
    Rig --> Tools[Tool/RAG agent workflows]
    Tools --> Pydantic[Pydantic validation boundary]
```

## Observability

```mermaid
flowchart TD
    App[PyBibX core/API/agents] --> Loguru[Loguru local logs]
    App --> Logfire[Logfire traces/metrics/evals]
    Logfire --> OTel[OpenTelemetry export]
    Mistral[mistral.rs runtime] --> Prometheus[Prometheus metrics]
    OTel --> External[Optional external observability backend]
```

## Semantic Graphs

```mermaid
flowchart LR
    Citations[CitationEdge models] --> CiTO[CiTO typed relations]
    CiTO --> RX[RustWorkX graph]
    RX --> Metrics[Main path, co-citation, coupling, brokerage]
    RX --> NX[NetworkX export compatibility]
    RX --> Viz[Plotly/Cosmograph/Reflex evaluation]
```

## CI And Tooling

```mermaid
flowchart LR
    Commit[Commit/PR] --> Pixi[Pixi env]
    Pixi --> UV[uv workspace checks]
    UV --> Ruff[Ruff format/check]
    UV --> Types[Pyright + ty]
    UV --> Tests[pytest + coverage + pytest-gremlins]
    UV --> Docs[Vale]
    UV --> Perf[Scalene targeted profiles]
    Tests --> Gates[Conductor phase gate]
    Renovate[Renovate] --> Commit
```

