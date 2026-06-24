# Review

Review completed on 2026-06-24 using Codex subagents after the Cline lane remained blocked by non-TTY configuration.

## Findings Fixed

- Default Great Expectations and Deepchecks suites only covered OpenAlex, Crossref, and PubMed instead of all registered providers with fixtures. The default quality plan now derives provider coverage from the provider registry.
- Pixi exposed only the ingestion Scalene profiling task. It now also exposes a graph profiling task for `pybibx/graph/builders.py`.
- Quality settings for Great Expectations, Deepchecks, Kedro, Scalene, and pytest-gremlins were defined but ignored by the default plan. The default plan now honors those enable flags.
- Kedro dependency validation accepted duplicate node outputs and self-consuming nodes. Pipeline validation now rejects both ambiguous graph shapes.
- The optional dependency import test loaded `pybibx.quality` before checking the import boundary. It now runs in a subprocess with optional quality, observability, performance, mutation, and legacy dependencies blocked.
- Closeout evidence was incomplete. This review file, index links, acceptance trace, and refreshed verification evidence were added before archive.

## Acceptance Trace

| Criterion | Evidence |
| --- | --- |
| `pybibx.quality` imports without optional quality dependencies installed. | `test_quality_package_imports_without_optional_quality_dependencies` blocks Great Expectations, Deepchecks, Kedro, Loguru, Logfire, OpenTelemetry, Prometheus client, Scalene, pytest-gremlins, and legacy heavy imports in a subprocess. |
| Great Expectations and Deepchecks suite specs are generated for provider fixtures. | `test_default_quality_observability_plan_combines_all_requested_lanes` verifies suite coverage for every registered provider with fixtures. |
| Kedro pipeline specs validate unique nodes and node-output dependencies. | `test_kedro_pipeline_validates_unique_nodes_and_node_output_dependencies` covers duplicate names, missing outputs, duplicate outputs, and self-consuming nodes. |
| Observability plans honor Loguru, Logfire, OpenTelemetry, OTLP endpoint, and Prometheus settings. | `test_observability_plan_respects_loguru_logfire_otel_and_prometheus_settings`. |
| Scalene and pytest-gremlins specs emit reviewable commands. | `test_scalene_and_pytest_gremlins_specs_generate_reviewable_commands`. |
| Pixi exposes mutation and profiling tasks. | `test_quality_tool_configs_are_present_and_scoped` covers mutation, ingestion profiling, and graph profiling tasks. |
| Local quality and type gates pass. | See `verification.md`. |

## Manual Checkpoint

- Expected files/settings/tests/docs were reviewed and updated for the Quality, Observability, Perf track.
- No unrelated files were intentionally changed.
- Acceptance criteria are mapped above and validated locally.
- Remaining blocker is external only until GitHub Actions has passed on the pushed closeout commit.
