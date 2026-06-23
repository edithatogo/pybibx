from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from pybibx.schemas.enums import ProviderName
from pybibx.versioning import CompatibilityProfile, VersionedSurface, VersionStamp, default_compatibility_profile


class StrictSettingsModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class ProviderSettings(StrictSettingsModel):
    provider: ProviderName
    api_key: SecretStr | None = None
    email: str | None = None
    base_url: str | None = None
    rate_limit_per_second: float = Field(default=1.0, gt=0)
    enabled: bool = True
    credential_required: bool = False


class RuntimeSettings(StrictSettingsModel):
    openai_compatible_base_url: str | None = None
    ollama_base_url: str = "http://localhost:11434/v1"
    mistral_rs_base_url: str | None = None
    default_model: str = "local"
    request_timeout_seconds: float = Field(default=60.0, gt=0)


class StorageSettings(StrictSettingsModel):
    root_path: Path = Path(".pybibx")
    cache_path: Path = Path(".pybibx/cache")
    vector_path: Path = Path(".pybibx/lancedb")
    output_path: Path = Path(".pybibx/outputs")


class ObservabilitySettings(StrictSettingsModel):
    log_level: str = "INFO"
    logfire_enabled: bool = False
    opentelemetry_enabled: bool = False
    prometheus_enabled: bool = False


class FeatureGateSettings(StrictSettingsModel):
    enable_legacy_runtime: bool = True
    enable_hosted_llms: bool = False
    enable_licensed_providers: bool = False
    enable_pdf_parsing: bool = False
    enable_agentic_rag: bool = False


class PyBibXSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        env_prefix="PYBIBX_",
        extra="ignore",
        frozen=True,
        str_strip_whitespace=True,
    )

    compatibility: CompatibilityProfile = Field(default_factory=default_compatibility_profile)
    providers: tuple[ProviderSettings, ...] = Field(
        default_factory=lambda: (
            ProviderSettings(provider=ProviderName.OPENALEX, rate_limit_per_second=10.0),
            ProviderSettings(provider=ProviderName.CROSSREF, rate_limit_per_second=5.0),
            ProviderSettings(provider=ProviderName.PUBMED, rate_limit_per_second=3.0),
            ProviderSettings(provider=ProviderName.SCOPUS, enabled=False, credential_required=True),
            ProviderSettings(provider=ProviderName.WEB_OF_SCIENCE, enabled=False, credential_required=True),
        ),
    )
    runtime: RuntimeSettings = Field(default_factory=RuntimeSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
    features: FeatureGateSettings = Field(default_factory=FeatureGateSettings)

    def provider_settings(self, provider: ProviderName) -> ProviderSettings | None:
        for item in self.providers:
            if item.provider is provider:
                return item
        return None


def load_settings() -> PyBibXSettings:
    return PyBibXSettings()


def settings_version_stamp() -> VersionStamp:
    return VersionStamp(surface=VersionedSurface.SETTINGS, name="pybibx-settings", version="1.0.0")
