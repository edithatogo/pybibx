# Review

Review completed on 2026-06-24 using Codex subagents after the Cline lane remained blocked by non-TTY configuration.

## Findings Fixed

- Hosted OpenAI-compatible endpoints could be selected while hosted LLMs were disabled. The plan now rejects non-local OpenAI-compatible endpoints unless `enable_hosted_llms` is true.
- mistral.rs metrics were derived by appending `/metrics` to the API path. Runtime settings now allow `mistral_rs_metrics_url`, and the default derivation uses the service origin.
- Public Instructor specs allowed blank or duplicate evidence identifiers. Evidence IDs are now non-empty and unique.
- PydanticAI plans could opt out of evidence enforcement. Agent plans now require PydanticAI evidence enforcement.
- Instructor specs could be mismatched with the task evidence set. Agent plans now require Instructor evidence IDs to match task evidence IDs.
- Evidence-required RAG plans could contain no usable legal routes. RAG plans now reject empty legal credential-free route sets when evidence is required.
- Optional AI import coverage was too weak because the test module imported `pybibx.ai` before the import-boundary assertion. The import test now runs in a subprocess with optional and legacy dependencies blocked.
- Optional AI extras were too coarse for backend-specific installation. Backend-specific AI extras were added while keeping the baseline import dependency-free.

## Acceptance Trace

| Criterion | Evidence |
| --- | --- |
| AI package imports without optional AI dependencies installed. | `test_ai_package_imports_without_optional_agent_dependencies` blocks PydanticAI, Instructor, DSPy, LlamaIndex, OpenAI, Ollama/mistral libraries, RAG optional deps, pandas, and legacy runtime imports. |
| Ollama is the default local OpenAI-compatible runtime. | `test_default_runtime_uses_ollama_openai_compatible_endpoint`. |
| mistral.rs can be selected when configured and exposes a metrics URL. | `test_mistral_rs_runtime_requires_configured_endpoint_and_exposes_metrics`. |
| OpenAI-compatible endpoints can be configured explicitly for local or hosted gateways. | `test_openai_compatible_runtime_supports_hosted_or_local_gate` and `test_hosted_openai_compatible_runtime_requires_feature_gate`. |
| Agent tasks fail closed without evidence sets. | `test_agent_task_and_instructor_specs_require_evidence`. |
| Instructor extraction specs fail closed without evidence identifiers. | `test_agent_task_and_instructor_specs_require_evidence` covers missing, blank, and duplicate IDs. |
| Default orchestration includes PydanticAI, Instructor, DSPy, and LlamaIndex components. | `test_default_plan_enables_pydanticai_instructor_dspy_and_llamaindex`. |
| Local quality and type gates pass. | See `verification.md`. |

## Manual Checkpoint

- Expected files/settings/tests/docs were reviewed and updated for the AI/Agent Layer, with one dependent evidence-route fix in the RAG layer.
- No unrelated files were intentionally changed.
- Acceptance criteria are mapped above and validated locally.
- Remaining blocker is external only until GitHub Actions has passed on the pushed closeout commit.
