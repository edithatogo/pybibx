# Product Definition

## Initial Concept

PyBibX is an existing bibliometric and scientometric Python library that ingests Scopus, Web of Science, PubMed, and OpenAlex exports; normalizes bibliographic entities; computes bibliometric, scientometric, graph, and AI-assisted analyses; and exposes both notebook/API and web-app workflows.

The PyBibX 6.0 roadmap is to turn the current monolithic, pandas-heavy, Flask-backed library into a strict, provider-aware, ontology-backed, observable, agentic research automation stack.

## Product Goal

PyBibX should remain approachable for researchers who import bibliographic files and run analyses, while gaining a modern internal architecture that can scale to large open knowledge graphs, legally process full text, validate all data contracts, and produce citation-safe AI-assisted outputs.

## Primary Users

- Bibliometrics and scientometrics researchers analyzing publication, citation, collaboration, and topic networks.
- Academic teams ingesting Scopus, Web of Science, PubMed, OpenAlex, Crossref, Semantic Scholar, and OpenCitations data.
- Research offices and institutional analysts who need reproducible, auditable research-impact and collaboration pipelines.
- Advanced users building full-text RAG, semantic citation graphs, or agentic report workflows over research corpora.

## Current Product Surface

- Python package `pybibx` version `5.9.2`, packaged with `setup.py`.
- Main package under `pybibx/base/`, including the `pbx_probe` analysis class, OpenAlex helpers, Flask web app, batch helpers, topic/graph modules, and stopword assets.
- Current dependency surface includes pandas, NetworkX, Flask, BERTopic, sentence-transformers, transformers, torch, scikit-learn, scipy, plotly, matplotlib, OpenAI, Gemini, and related NLP/visualization libraries.

## Target Product Surface

- A versioned Python library API with compatibility adapters for legacy `pbx_probe` workflows.
- Provider-specific ingestion adapters returning validated, versioned, normalized data.
- Semantic citation graph capabilities using ontology-backed edge types.
- Legal full-text ingestion and RAG with verified evidence sets.
- Local-first and air-gapped execution paths.
- Observable, typed, structured AI workflows that fail closed when sources or schemas cannot be verified.

