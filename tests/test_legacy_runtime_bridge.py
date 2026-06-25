"""Regression tests for the maintained-to-legacy runtime bridge."""

from __future__ import annotations

import subprocess
import sys
from typing import Any, cast

import pandas as pd
import pytest

from pybibx.legacy import (
    LEGACY_DATAFRAME_COLUMNS,
    LegacyBridgeError,
    legacy_dataframe_to_citations,
    legacy_dataframe_to_export_manifest,
    legacy_dataframe_to_works,
    require_supported_legacy_analysis,
    works_to_legacy_dataframe,
)
from pybibx.schemas import Author, Citation, Institution, OutputFormat, ProviderName, Work

LEGACY_YEAR = 2025
LEGACY_CITATION_COUNT = 12


def test_bridge_import_does_not_load_legacy_runtime() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import pybibx.legacy;"
                "assert 'pybibx.base.pbx' not in sys.modules;"
                "assert 'flask' not in sys.modules"
            ),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert completed.stderr == ""


def test_works_to_legacy_dataframe_can_bootstrap_existing_probe() -> None:
    work = Work(
        work_id="W-legacy-bridge",
        title="A normalized bridge fixture",
        doi="https://doi.org/10.1234/bridge.fixture",
        publication_year=2026,
        authors=(
            Author(display_name="Ada Lovelace"),
            Author(display_name="Grace Hopper"),
        ),
        institutions=(Institution(display_name="Example University", country_code="NZ"),),
        concepts=("bibliometrics", "pipelines"),
        sustainable_development_goals=("SDG 9",),
        citation_count=7,
        source_provider=ProviderName.OPENALEX,
    )

    citation = Citation(
        source_work_id=work.work_id,
        target_work_id="W-target",
        source_doi=work.doi,
        target_doi="10.5678/target.fixture",
    )

    frame = works_to_legacy_dataframe((work,), citations=(citation,))

    assert tuple(frame.columns) == LEGACY_DATAFRAME_COLUMNS
    assert frame.loc[0, "author"] == "Ada Lovelace and Grace Hopper"
    assert frame.loc[0, "doi"] == "10.1234/bridge.fixture"
    assert frame.loc[0, "note"] == "Cited by: 7"
    assert frame.loc[0, "author_keywords"] == "bibliometrics; pipelines"
    assert frame.loc[0, "references"] == "10.5678/target.fixture"
    assert frame.loc[0, "country"] == "NZ"
    assert frame.loc[0, "pybibx_schema_version"] == work.compatibility.schema_profile.version

    from pybibx import pbx_probe  # noqa: PLC0415 - legacy runtime is loaded only for this smoke path.

    probe = cast("Any", pbx_probe(data=frame, db="scopus"))

    assert probe.data.shape[0] == 1
    assert probe.citation == [7]
    assert probe.data.loc[0, "title"] == "A normalized bridge fixture"
    assert probe.table_id_doc.loc[0, "ID"] == "0"


def test_legacy_dataframe_to_works_normalizes_common_export_columns() -> None:
    frame = pd.DataFrame(
        [
            {
                "Title": "Legacy export row",
                "Authors": "Ada Lovelace and Grace Hopper",
                "Year": str(LEGACY_YEAR),
                "DOI": "doi:10.4321/legacy.export",
                "Citations": f"Cited by: {LEGACY_CITATION_COUNT}",
                "Document Type": "Article",
                "Author Keywords": "bibliometrics; scientometrics",
                "Institution": "Example University",
                "Country": "au",
                "References": "10.5555/ref.one; Legacy reference without DOI",
            },
        ],
    )

    works = legacy_dataframe_to_works(frame, source_provider=ProviderName.SCOPUS)
    citations = legacy_dataframe_to_citations(frame)
    manifest = legacy_dataframe_to_export_manifest(frame, output_format=OutputFormat.JSONL)

    assert len(works) == 1
    assert works[0].title == "Legacy export row"
    assert works[0].doi == "10.4321/legacy.export"
    assert works[0].publication_year == LEGACY_YEAR
    assert [author.display_name for author in works[0].authors] == ["Ada Lovelace", "Grace Hopper"]
    assert works[0].institutions[0].country_code == "AU"
    assert works[0].citation_count == LEGACY_CITATION_COUNT
    assert works[0].source_provider is ProviderName.SCOPUS
    assert works[0].compatibility.input is not None
    assert works[0].compatibility.input.version == "legacy-runtime"
    assert [citation.target_work_id for citation in citations] == ["10.5555/ref.one", "Legacy reference without DOI"]
    assert citations[0].source_work_id == "10.4321/legacy.export"
    assert citations[0].target_doi == "10.5555/ref.one"
    assert citations[1].target_doi is None
    assert manifest.record_count == 1
    assert manifest.output_format is OutputFormat.JSONL


def test_legacy_dataframe_to_works_fails_closed_for_missing_or_invalid_fields() -> None:
    with pytest.raises(LegacyBridgeError, match="title column"):
        legacy_dataframe_to_works(pd.DataFrame([{"DOI": "10.1234/missing.title"}]))

    with pytest.raises(LegacyBridgeError, match="failed to convert legacy row 0"):
        legacy_dataframe_to_works(pd.DataFrame([{"Title": "Bad DOI", "DOI": "not-a-doi"}]))

    with pytest.raises(LegacyBridgeError, match="references column"):
        legacy_dataframe_to_citations(pd.DataFrame([{"Title": "No references"}]))


def test_unsupported_legacy_paths_fail_with_clear_error() -> None:
    require_supported_legacy_analysis("citation-counts")

    with pytest.raises(LegacyBridgeError, match="not supported"):
        require_supported_legacy_analysis("full-text-rag")
