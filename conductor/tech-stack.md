# Technology Stack

## Current Stack

- Language: Python.
- Packaging: `setup.py` with setuptools.
- Dataframes and numeric computing: pandas, numpy, scipy, scikit-learn.
- Graphs: NetworkX.
- Web app: Flask.
- Visualization: plotly, matplotlib, wordcloud.
- NLP and AI: BERTopic, KeyBERT, gensim, sentence-transformers, transformers, torch, OpenAI, Google Gemini, PEGASUS/BERT summarization.
- Data sources: Scopus, Web of Science, PubMed, OpenAlex exports/API.

## Target Stack

- Environment and packaging: Pixi environment plus uv workspace/package management.
- Python target: latest stable CPython only for the 6.0 refactor line.
- Linting and type checking: Ruff strict, Pyright, ty strict.
- Tests and quality: pytest, coverage, pytest-gremlins, Scalene, Vale, TestSprite, Renovate, Ruff Action.
- Schemas and settings: Pydantic v2, pydantic-settings, Jiter, JSON Schema snapshots.
- Data processing: Polars lazy/streaming, Arrow-compatible storage paths.
- Graphs: RustWorkX primary, NetworkX compatibility/export, later evaluation of Graphina, PyBiblioNet, and PyG.
- Providers: OpenAlex, Crossref, PubMed/MEDLINE, OpenCitations, Semantic Scholar, ROR, ORCID, Unpaywall, arXiv, bioRxiv, medRxiv, Google Scholar export import, Scopus, Web of Science, Embase, EBSCO, ProQuest/Ovid.
- Ontologies and exchange: SPAR/CiTO/FaBiO/FRAPO/PSO/ORG, OpenAlex/Schema.org, ROR, ORCID, CSL-JSON, BibTeX, RIS, Obsidian/BibLib-style Markdown.
- AI and RAG: PydanticAI, Instructor, DSPy, LlamaIndex, FastEmbed, LanceDB, Docling/PDFMux evaluation, Ollama, mistral.rs, optional Rig, optional Monty.
- Observability: Loguru, Pydantic Logfire, OpenTelemetry, optional Prometheus metrics from local runtimes.
- Pipelines and data quality: Kedro, Great Expectations, Deepchecks.
- UI/API: FastAPI, Reflex evaluation, Cosmograph evaluation, legacy Flask compatibility boundary.
- Agent orchestration: Codex CLI with `gpt-5.5` for orchestration/review, Cline CLI with `deepseek-v4-flash` for external worker lanes when configured, and in-session multi-agent tools for Codex swarm fallback.

## Verify Before Pinning

- Una: exact package/source not yet confirmed.
- Mantra: exact package/source not yet confirmed; Logfire is the planned Pydantic-native observability layer.
- PDFMux and commercial/licensed services: evaluate availability, terms, and local/offline alternatives before depending on them.
