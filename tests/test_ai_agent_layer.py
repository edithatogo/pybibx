"""Regression tests for optional AI and agent orchestration contracts."""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from pybibx.ai import (
    AgentFramework,
    AgentOrchestrationPlan,
    LocalRuntimeKind,
    build_local_runtime,
    create_agent_task,
    create_instructor_extraction_spec,
    default_agent_orchestration_plan,
)
from pybibx.rag import build_evidence_set, chunk_markdown
from pybibx.settings import PyBibXSettings, RuntimeSettings

if TYPE_CHECKING:
    from pybibx.schemas import EvidenceSet


def _evidence_set() -> EvidenceSet:
    chunks = chunk_markdown(
        work_id="W1",
        source_locator="https://example.test/paper.pdf",
        markdown="# Results\nThe paper reports a supported finding.",
    )
    return build_evidence_set(
        evidence_set_id="evidence:1",
        claim_text="The paper reports a supported finding.",
        chunks=chunks,
        supporting_chunk_ids=(chunks[0].chunk_id,),
    )


def test_ai_package_imports_without_optional_agent_dependencies() -> None:
    module = importlib.import_module("pybibx.ai")

    assert module.AgentFramework.PYDANTIC_AI.value == "pydantic-ai"


def test_default_runtime_uses_ollama_openai_compatible_endpoint() -> None:
    runtime = build_local_runtime(PyBibXSettings())

    assert runtime.kind is LocalRuntimeKind.OLLAMA
    assert runtime.base_url == "http://localhost:11434/v1"
    assert runtime.openai_compatible is True
    assert runtime.model == "local"


def test_mistral_rs_runtime_requires_configured_endpoint_and_exposes_metrics() -> None:
    settings = PyBibXSettings(
        runtime=RuntimeSettings(
            mistral_rs_base_url="http://localhost:1234/v1",
            default_model="mistral-rs:local-mistral",
        ),
    )
    runtime = build_local_runtime(settings)

    assert runtime.kind is LocalRuntimeKind.MISTRAL_RS
    assert runtime.model == "local-mistral"
    assert runtime.supports_vision is True
    assert runtime.metrics_url == "http://localhost:1234/v1/metrics"

    with pytest.raises(ValueError, match="mistral_rs_base_url"):
        build_local_runtime(PyBibXSettings(), kind=LocalRuntimeKind.MISTRAL_RS)


def test_openai_compatible_runtime_supports_hosted_or_local_gate() -> None:
    settings = PyBibXSettings(
        runtime=RuntimeSettings(
            openai_compatible_base_url="http://localhost:8080/v1",
            default_model="openai-compatible:research-model",
        ),
    )
    runtime = build_local_runtime(settings)

    assert runtime.kind is LocalRuntimeKind.OPENAI_COMPATIBLE
    assert runtime.model == "research-model"


def test_agent_task_and_instructor_specs_require_evidence() -> None:
    evidence = _evidence_set()
    task = create_agent_task(
        task_id="task:1",
        instruction="Extract an evidence-grounded claim.",
        evidence_sets=(evidence,),
    )
    instructor = create_instructor_extraction_spec(response_model="GroundedExtraction", evidence_sets=(evidence,))

    assert task.evidence_sets == (evidence,)
    assert instructor.framework is AgentFramework.INSTRUCTOR
    assert instructor.evidence_set_ids == (evidence.evidence_set_id,)

    with pytest.raises(ValueError, match="at least one evidence"):
        create_agent_task(task_id="bad", instruction="No evidence", evidence_sets=())

    with pytest.raises(ValidationError, match="evidence_set_ids"):
        create_instructor_extraction_spec(response_model="GroundedExtraction", evidence_sets=())


def test_default_plan_enables_pydanticai_instructor_dspy_and_llamaindex() -> None:
    evidence = _evidence_set()
    task = create_agent_task(
        task_id="task:rag",
        instruction="Synthesize a source-grounded result.",
        evidence_sets=(evidence,),
    )
    plan = default_agent_orchestration_plan(task=task)

    assert plan.frameworks == (
        AgentFramework.PYDANTIC_AI,
        AgentFramework.INSTRUCTOR,
        AgentFramework.DSPY,
        AgentFramework.LLAMA_INDEX,
    )
    assert plan.pydantic_ai.result_schema == "GroundedExtraction"
    assert plan.instructor.evidence_set_ids == ("evidence:1",)
    assert plan.dspy is not None
    assert plan.dspy.signature_name == "ExtractEvidenceGroundedClaim"
    assert plan.llama_index is not None
    assert plan.llama_index.vector_backend == "lancedb"


def test_plan_frameworks_fail_closed_when_components_do_not_match() -> None:
    evidence = _evidence_set()
    task = create_agent_task(task_id="task:bad", instruction="Bad plan", evidence_sets=(evidence,))
    plan = default_agent_orchestration_plan(task=task)

    with pytest.raises(ValidationError, match="frameworks must match"):
        AgentOrchestrationPlan(
            task=plan.task,
            runtime=plan.runtime,
            pydantic_ai=plan.pydantic_ai,
            instructor=plan.instructor,
            dspy=plan.dspy,
            llama_index=plan.llama_index,
            frameworks=(AgentFramework.PYDANTIC_AI,),
        )
