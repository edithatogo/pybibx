from __future__ import annotations

from enum import StrEnum
from ipaddress import ip_address
from typing import TYPE_CHECKING, Annotated, Self
from urllib.parse import urlparse

from pydantic import Field, model_validator

from pybibx.schemas import EvidenceSet  # noqa: TC001 - Pydantic resolves this model at runtime.
from pybibx.schemas.records import StrictSchemaModel
from pybibx.settings import PyBibXSettings
from pybibx.versioning import CompatibilityProfile, VersionedSurface, VersionStamp, default_compatibility_profile

if TYPE_CHECKING:
    from collections.abc import Sequence

OLLAMA_MODEL_PREFIX = "ollama:"
MISTRAL_RS_MODEL_PREFIX = "mistral-rs:"
OPENAI_COMPATIBLE_MODEL_PREFIX = "openai-compatible:"
LOCAL_RUNTIME_HOSTS = frozenset({"localhost"})


class AgentFramework(StrEnum):
    PYDANTIC_AI = "pydantic-ai"
    INSTRUCTOR = "instructor"
    DSPY = "dspy"
    LLAMA_INDEX = "llama-index"


class LocalRuntimeKind(StrEnum):
    OLLAMA = "ollama"
    MISTRAL_RS = "mistral.rs"
    OPENAI_COMPATIBLE = "openai-compatible"


class LocalRuntime(StrictSchemaModel):
    kind: LocalRuntimeKind
    base_url: str = Field(min_length=1)
    model: str = Field(min_length=1)
    request_timeout_seconds: float = Field(gt=0)
    openai_compatible: bool = True
    supports_embeddings: bool = True
    supports_vision: bool = False
    metrics_url: str | None = None

    @model_validator(mode="after")
    def metrics_match_runtime(self) -> Self:
        if self.kind is LocalRuntimeKind.MISTRAL_RS and self.metrics_url is None:
            msg = "mistral.rs runtimes must declare metrics_url"
            raise ValueError(msg)
        if self.metrics_url is not None and self.kind is not LocalRuntimeKind.MISTRAL_RS:
            msg = "metrics_url is currently reserved for mistral.rs runtimes"
            raise ValueError(msg)
        return self


class PydanticAgentSpec(StrictSchemaModel):
    framework: AgentFramework = AgentFramework.PYDANTIC_AI
    result_schema: str = Field(min_length=1)
    retries: int = Field(default=2, ge=0)
    require_evidence: bool = True


class InstructorExtractionSpec(StrictSchemaModel):
    framework: AgentFramework = AgentFramework.INSTRUCTOR
    response_model: str = Field(min_length=1)
    retry_on_validation_error: bool = True
    streaming_partial_objects: bool = False
    evidence_set_ids: tuple[Annotated[str, Field(min_length=1)], ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def evidence_is_explicit(self) -> Self:
        if not self.evidence_set_ids:
            msg = "Instructor extraction specs must declare evidence_set_ids"
            raise ValueError(msg)
        if len(set(self.evidence_set_ids)) != len(self.evidence_set_ids):
            msg = "Instructor extraction evidence_set_ids must be unique"
            raise ValueError(msg)
        return self


class DspyProgramSpec(StrictSchemaModel):
    framework: AgentFramework = AgentFramework.DSPY
    signature_name: str = Field(min_length=1)
    optimizer: str = "bootstrap-fewshot"
    metric_name: str = "evidence-grounded-correctness"
    training_example_count: int = Field(default=0, ge=0)


class LlamaIndexRagSpec(StrictSchemaModel):
    framework: AgentFramework = AgentFramework.LLAMA_INDEX
    index_name: str = Field(min_length=1)
    vector_backend: str = "lancedb"
    embedding_backend: str = "fastembed"
    require_source_nodes: bool = True


class AgentTask(StrictSchemaModel):
    task_id: str = Field(min_length=1)
    instruction: str = Field(min_length=1)
    evidence_sets: tuple[EvidenceSet, ...] = Field(min_length=1)
    compatibility: CompatibilityProfile = Field(default_factory=default_compatibility_profile)


class AgentOrchestrationPlan(StrictSchemaModel):
    task: AgentTask
    runtime: LocalRuntime
    pydantic_ai: PydanticAgentSpec
    instructor: InstructorExtractionSpec
    dspy: DspyProgramSpec | None = None
    llama_index: LlamaIndexRagSpec | None = None
    frameworks: tuple[AgentFramework, ...]
    allow_hosted_llms: bool = False

    @model_validator(mode="after")
    def plan_frameworks_match_components(self) -> Self:
        expected = {AgentFramework.PYDANTIC_AI, AgentFramework.INSTRUCTOR}
        if self.dspy is not None:
            expected.add(AgentFramework.DSPY)
        if self.llama_index is not None:
            expected.add(AgentFramework.LLAMA_INDEX)
        if set(self.frameworks) != expected:
            msg = f"frameworks must match enabled components: {sorted(item.value for item in expected)}"
            raise ValueError(msg)
        if self.allow_hosted_llms and self.runtime.kind is not LocalRuntimeKind.OPENAI_COMPATIBLE:
            msg = "hosted LLM use must go through an explicit OpenAI-compatible runtime"
            raise ValueError(msg)
        if (
            not self.allow_hosted_llms
            and self.runtime.kind is LocalRuntimeKind.OPENAI_COMPATIBLE
            and _is_hosted_openai_compatible_base_url(self.runtime.base_url)
        ):
            msg = "hosted OpenAI-compatible runtimes require enable_hosted_llms"
            raise ValueError(msg)
        if not self.pydantic_ai.require_evidence:
            msg = "PydanticAI orchestration must require evidence"
            raise ValueError(msg)
        expected_evidence_ids = {item.evidence_set_id for item in self.task.evidence_sets}
        if set(self.instructor.evidence_set_ids) != expected_evidence_ids:
            msg = "Instructor evidence_set_ids must match task evidence_sets"
            raise ValueError(msg)
        return self


def build_local_runtime(settings: PyBibXSettings, *, kind: LocalRuntimeKind | None = None) -> LocalRuntime:
    runtime = settings.runtime
    selected = kind or _default_runtime_kind(settings)
    if selected is LocalRuntimeKind.MISTRAL_RS:
        if runtime.mistral_rs_base_url is None:
            msg = "mistral.rs runtime requested but mistral_rs_base_url is not configured"
            raise ValueError(msg)
        return LocalRuntime(
            kind=LocalRuntimeKind.MISTRAL_RS,
            base_url=runtime.mistral_rs_base_url,
            model=_strip_model_prefix(runtime.default_model, MISTRAL_RS_MODEL_PREFIX),
            request_timeout_seconds=runtime.request_timeout_seconds,
            supports_vision=True,
            metrics_url=runtime.mistral_rs_metrics_url or _derive_mistral_rs_metrics_url(runtime.mistral_rs_base_url),
        )
    if selected is LocalRuntimeKind.OPENAI_COMPATIBLE:
        if runtime.openai_compatible_base_url is None:
            msg = "OpenAI-compatible runtime requested but openai_compatible_base_url is not configured"
            raise ValueError(msg)
        return LocalRuntime(
            kind=LocalRuntimeKind.OPENAI_COMPATIBLE,
            base_url=runtime.openai_compatible_base_url,
            model=_strip_model_prefix(runtime.default_model, OPENAI_COMPATIBLE_MODEL_PREFIX),
            request_timeout_seconds=runtime.request_timeout_seconds,
        )
    return LocalRuntime(
        kind=LocalRuntimeKind.OLLAMA,
        base_url=runtime.ollama_base_url,
        model=_strip_model_prefix(runtime.default_model, OLLAMA_MODEL_PREFIX),
        request_timeout_seconds=runtime.request_timeout_seconds,
    )


def create_agent_task(
    *,
    task_id: str,
    instruction: str,
    evidence_sets: Sequence[EvidenceSet],
) -> AgentTask:
    if not evidence_sets:
        msg = "agent tasks require at least one evidence set"
        raise ValueError(msg)
    return AgentTask(
        task_id=task_id,
        instruction=instruction,
        evidence_sets=tuple(evidence_sets),
        compatibility=CompatibilityProfile(
            ontology=(VersionStamp(surface=VersionedSurface.SCHEMA, name="agent-task", version="1.0.0"),),
        ),
    )


def create_instructor_extraction_spec(
    *,
    response_model: str,
    evidence_sets: Sequence[EvidenceSet],
    streaming_partial_objects: bool = False,
) -> InstructorExtractionSpec:
    return InstructorExtractionSpec(
        response_model=response_model,
        evidence_set_ids=tuple(item.evidence_set_id for item in evidence_sets),
        streaming_partial_objects=streaming_partial_objects,
    )


def default_agent_orchestration_plan(
    *,
    task: AgentTask,
    settings: PyBibXSettings | None = None,
    runtime_kind: LocalRuntimeKind | None = None,
    enable_dspy: bool = True,
    enable_llama_index: bool = True,
) -> AgentOrchestrationPlan:
    app_settings = settings or PyBibXSettings()
    runtime = build_local_runtime(app_settings, kind=runtime_kind)
    instructor = create_instructor_extraction_spec(
        response_model="GroundedExtraction",
        evidence_sets=task.evidence_sets,
    )
    dspy = (
        DspyProgramSpec(signature_name="ExtractEvidenceGroundedClaim", training_example_count=len(task.evidence_sets))
        if enable_dspy
        else None
    )
    llama_index = LlamaIndexRagSpec(index_name=f"{task.task_id}-rag") if enable_llama_index else None
    frameworks = [AgentFramework.PYDANTIC_AI, AgentFramework.INSTRUCTOR]
    if dspy is not None:
        frameworks.append(AgentFramework.DSPY)
    if llama_index is not None:
        frameworks.append(AgentFramework.LLAMA_INDEX)
    return AgentOrchestrationPlan(
        task=task,
        runtime=runtime,
        pydantic_ai=PydanticAgentSpec(result_schema="GroundedExtraction"),
        instructor=instructor,
        dspy=dspy,
        llama_index=llama_index,
        frameworks=tuple(frameworks),
        allow_hosted_llms=app_settings.features.enable_hosted_llms,
    )


def _default_runtime_kind(settings: PyBibXSettings) -> LocalRuntimeKind:
    model = settings.runtime.default_model
    if model.startswith(MISTRAL_RS_MODEL_PREFIX) or settings.runtime.mistral_rs_base_url is not None:
        return LocalRuntimeKind.MISTRAL_RS
    if model.startswith(OPENAI_COMPATIBLE_MODEL_PREFIX) or settings.runtime.openai_compatible_base_url is not None:
        return LocalRuntimeKind.OPENAI_COMPATIBLE
    return LocalRuntimeKind.OLLAMA


def _strip_model_prefix(model: str, prefix: str) -> str:
    stripped = model.removeprefix(prefix)
    return stripped or "local"


def _derive_mistral_rs_metrics_url(base_url: str) -> str:
    parsed = urlparse(base_url)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}/metrics"
    return f"{base_url.rstrip('/')}/metrics"


def _is_hosted_openai_compatible_base_url(base_url: str) -> bool:
    hostname = urlparse(base_url).hostname
    if hostname is None:
        return False
    return not _is_local_runtime_hostname(hostname)


def _is_local_runtime_hostname(hostname: str) -> bool:
    normalized = hostname.lower()
    if normalized in LOCAL_RUNTIME_HOSTS or normalized.endswith(".local"):
        return True
    try:
        parsed_ip = ip_address(normalized)
    except ValueError:
        return False
    return parsed_ip.is_loopback or parsed_ip.is_private or parsed_ip.is_link_local
