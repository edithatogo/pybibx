# PyBibX 6.0 Alpha Release Readiness

PyBibX 6.0 alpha is a maintained refactor line on top of the PyBibX 5.9.2 package identity. It is ready for early local evaluation of typed schemas, provider fixtures, ingestion, graph, RAG planning, AI orchestration contracts, report exports, quality plans, and the legacy bridge. It is not a PyPI publishing event unless a maintainer explicitly requests a tag and release.

## Public Surface

| Surface | Status | Notes |
|---|---|---|
| `pybibx` | Legacy compatibility | Keeps lazy `pbx_probe`, `bibliometrix`, `web_app`, and `web_stop` boundaries. |
| `pybibx.schemas` | Public alpha | Pydantic v2 records for `Work`, `Author`, `Institution`, `Citation`, evidence, exports, and ontology facets. |
| `pybibx.settings` | Public alpha | Pydantic-settings configuration for providers, quality lanes, AI, RAG, reports, and observability. |
| `pybibx.release` | Public alpha | Machine-readable release boundary used by tests and release-readiness docs. |
| `pybibx.providers` | Public alpha | Registry metadata for open, export-only, and credential-gated data sources. |
| `pybibx.pipeline` | Public alpha | Offline provider pipeline for local fixtures and exports. |
| `pybibx.legacy` | Public alpha | Adapters between maintained records and the legacy pandas `pbx_probe` runtime. |
| `pybibx.graph` | Provisional | RustWorkX graph builders with NetworkX export compatibility. |
| `pybibx.ingestion` | Provisional | Polars/Jiter parsers for maintained normalized records. |
| `pybibx.reports` | Provisional | Citation-safe Markdown, CSL-JSON, BibTeX, RIS, and BibLib-style export contracts. |
| `pybibx.quality` | Provisional | Great Expectations, Deepchecks, Kedro, Loguru/Logfire, OTel, Scalene, and pytest-gremlins planning contracts. |
| `pybibx.rag` | Optional | Legal full-text routing and local RAG planning contracts. |
| `pybibx.ai` | Optional | PydanticAI, Instructor, DSPy, LlamaIndex, Ollama, and mistral.rs orchestration contracts. |
| `pybibx.base` | Legacy | Existing analysis engine; excluded from strict 6.0 lint/type gates. |
| `pybibx.base.*` | Internal | Implementation modules under the legacy runtime are not part of the maintained alpha API. |

## Optional-Extra Compatibility Matrix

| Path | Command | Status | Boundary |
|---|---|---|---|
| Baseline | `uv sync --group dev` | Baseline-safe | CI-supported Python 3.14 path. |
| Quality | `uv sync --extra quality --group dev` | Optional | Great Expectations, Deepchecks, and Kedro planning. |
| AI | `uv sync --extra ai --group dev` | Optional | Hosted and local AI orchestration contracts; credentials remain user-provided. |
| RAG | `uv sync --extra rag --group dev` | Optional | Docling, FastEmbed, and LanceDB planning lane. |
| Reports | `uv sync --extra reports --group dev` | Optional | No heavy dependency today; marks export surface intent. |
| UI | `uv sync --extra ui --group dev` | Probing only | Reflex evaluation, not a production UI claim. |
| Legacy | `uv sync --extra legacy --group dev` | Probing only | Legacy NLP/UI stack; not baseline-safe on Python 3.14. |
| Licensed providers | `uv sync --group dev` | Credential-gated | Scopus and Web of Science require user-provided credentials. |
| All extras | `uv sync --all-extras --group dev` | Blocked for baseline | Kept out of CI while legacy NLP dependencies can fail on Python 3.14. |

## Release Notes

Completed Conductor tracks now cover packaging/tooling, schemas/settings/versioning, provider registry fixtures, Polars/Jiter ingestion, ontology graph core, full-text RAG planning, AI/agent orchestration, quality/observability/performance, UI/report contracts, provider pipeline, and the legacy runtime bridge.

Known limitations and blockers:

- PyPI publishing and tag creation are out of scope without explicit maintainer instruction.
- Scopus and Web of Science live connectors remain credential-gated.
- Google Scholar remains export/import-only; default scraping is not supported.
- Cline with `deepseek-v4-flash` remains blocked from this non-TTY Codex session.
- Hosted LLMs, Reflex, Cosmograph, Rig, Graphina, PyG, PDFMux, and Monty are not production-ready claims unless separately verified.

## Local Release Checks

```bash
uv lock --check
uv run --group dev pytest tests -q
uv run --group dev ruff check pybibx setup.py tests
uv run --group dev ruff format --check pybibx setup.py tests
uv run --group dev pyright
uv run --group dev ty check pybibx/__init__.py pybibx/release.py
uv run --group dev python -m build --wheel
vale docs conductor README.md
```
