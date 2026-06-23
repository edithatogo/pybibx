from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from pybibx import __version__


class VersionedSurface(StrEnum):
    LIBRARY = "library"
    SCHEMA = "schema"
    PROVIDER = "provider"
    INPUT = "input"
    OUTPUT = "output"
    ONTOLOGY = "ontology"
    SETTINGS = "settings"


class VersionStamp(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    surface: VersionedSurface
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)


class CompatibilityProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    library: VersionStamp = Field(
        default_factory=lambda: VersionStamp(surface=VersionedSurface.LIBRARY, name="pybibx", version=__version__),
    )
    schema_profile: VersionStamp = Field(
        default_factory=lambda: VersionStamp(
            surface=VersionedSurface.SCHEMA,
            name="normalized-records",
            version="1.0.0",
        ),
    )
    provider: VersionStamp | None = None
    input: VersionStamp | None = None
    output: VersionStamp | None = None
    ontology: tuple[VersionStamp, ...] = Field(default_factory=tuple)
    settings: VersionStamp = Field(
        default_factory=lambda: VersionStamp(
            surface=VersionedSurface.SETTINGS,
            name="pybibx-settings",
            version="1.0.0",
        ),
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


def default_compatibility_profile() -> CompatibilityProfile:
    return CompatibilityProfile()
