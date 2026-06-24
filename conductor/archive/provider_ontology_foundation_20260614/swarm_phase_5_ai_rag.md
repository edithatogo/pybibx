# Swarm Phase 5 Evidence: AI, RAG, And Local Execution

Agent: `019ecba7-a3fb-7dc2-a64f-4fa30ba13201`

## Findings

- Current AI paths use string prompts and lazy OpenAI/Gemini-style calls.
- No evidence-set contracts exist for generated reports or `ask_gpt_*` artifacts.
- Current dependencies do not include PydanticAI, Instructor, DSPy, LlamaIndex, FastEmbed, LanceDB, Docling, PDFMux, Ollama clients, or mistral.rs bridge code.

## Implementation Shape

- Use PydanticAI as the primary typed agent boundary.
- Use Instructor only for focused LLM-to-Pydantic extraction and retries.
- Add DSPy after baseline prompts and eval fixtures exist.
- Keep LlamaIndex optional for RAG orchestration, with Pydantic evidence validation as the final gate.
- Support Ollama first for local OpenAI-compatible endpoints.
- Add mistral.rs for stronger local serving where OpenAI/Anthropic-compatible endpoints and Prometheus metrics matter.
- Keep Rig optional and Rust-side only.
- Keep Monty experimental and optional.
- Add legal full-text resolver with source kind, license, URL, provider terms, retrieval time, and reuse flag.
- Evaluate Docling and PDFMux behind a common parser interface.
- Use FastEmbed and LanceDB for local evidence indexing.

## Acceptance Criteria

- Claims cannot serialize unless backed by verified evidence.
- Local runtimes are feature-gated and skip cleanly when unavailable.
- Parser fixtures cover born-digital, two-column, table-heavy, and scanned/OCR cases.
- Legacy `ask_chatgpt_*` and `ask_gemini_*` APIs are preserved or wrapped with migration notes.

## Blockers

- Dependency policy and schema/evidence contracts are prerequisites.
- Local Ollama/mistral.rs availability has not been verified.
- PDFMux maturity and terms need evidence before default use.
- Legal routing must record license/provider terms per source.

