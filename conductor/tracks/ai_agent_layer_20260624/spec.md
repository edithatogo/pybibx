# Spec

## Goals

- Add typed orchestration contracts for PydanticAI as the primary agent boundary.
- Add Instructor extraction contracts that require evidence-set identifiers.
- Add DSPy program specs for prompt/program optimization.
- Add LlamaIndex RAG specs for optional retrieval orchestration.
- Support local Ollama and mistral.rs OpenAI-compatible runtimes.
- Keep PydanticAI, Instructor, DSPy, and LlamaIndex optional dependencies rather than baseline imports.

## Non-Goals

- No live LLM calls in this track.
- No mandatory installation of optional AI packages for baseline PyBibX imports.
- No hosted LLM enablement by default.
- No Rig/Rust bridge implementation in this track.

## Acceptance

- The AI package imports without optional AI dependencies installed.
- Ollama is the default local OpenAI-compatible runtime.
- mistral.rs can be selected when configured and exposes a metrics URL.
- OpenAI-compatible endpoints can be configured explicitly for local or hosted gateways.
- Agent tasks fail closed without evidence sets.
- Instructor extraction specs fail closed without evidence identifiers.
- Default orchestration includes PydanticAI, Instructor, DSPy, and LlamaIndex components.
- Local quality and type gates pass.

