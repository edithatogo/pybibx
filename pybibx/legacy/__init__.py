"""Compatibility adapters between maintained schemas and the legacy runtime."""

from pybibx.legacy.bridge import (
    LEGACY_DATAFRAME_COLUMNS,
    SUPPORTED_LEGACY_ANALYSES,
    UNSUPPORTED_LEGACY_ANALYSES,
    LegacyBridgeDiagnostic,
    LegacyBridgeError,
    legacy_dataframe_to_export_manifest,
    legacy_dataframe_to_works,
    require_supported_legacy_analysis,
    works_to_legacy_dataframe,
)

__all__ = [
    "LEGACY_DATAFRAME_COLUMNS",
    "SUPPORTED_LEGACY_ANALYSES",
    "UNSUPPORTED_LEGACY_ANALYSES",
    "LegacyBridgeDiagnostic",
    "LegacyBridgeError",
    "legacy_dataframe_to_export_manifest",
    "legacy_dataframe_to_works",
    "require_supported_legacy_analysis",
    "works_to_legacy_dataframe",
]
