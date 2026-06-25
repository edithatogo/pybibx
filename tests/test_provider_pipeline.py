"""Regression tests for the maintained provider pipeline."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from pybibx.pipeline import (
    PipelineError,
    PipelineOutputFormat,
    ProviderPipelineRequest,
    export_provider_pipeline_result,
    run_provider_pipeline,
)
from pybibx.providers import DEFAULT_PROVIDER_REGISTRY
from pybibx.schemas import OutputFormat, ProviderName
from pybibx.settings import ProviderSettings, PyBibXSettings
from pybibx.versioning import VersionedSurface

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "tests" / "fixtures" / "providers"
OPEN_PROVIDER_FIXTURE_COUNT = 4


def test_offline_pipeline_normalizes_open_provider_fixtures() -> None:
    result = run_provider_pipeline(
        ProviderPipelineRequest(
            inputs={
                ProviderName.OPENALEX: FIXTURES / "openalex.json",
                ProviderName.CROSSREF: FIXTURES / "crossref.json",
                ProviderName.PUBMED: FIXTURES / "pubmed.json",
                ProviderName.MEDLINE: FIXTURES / "medline.json",
            },
        ),
    )

    assert [item.provider for item in result.sources] == [
        ProviderName.OPENALEX,
        ProviderName.CROSSREF,
        ProviderName.PUBMED,
        ProviderName.MEDLINE,
    ]
    assert [work.title for work in result.works] == [
        "OpenAlex fixture work",
        "Crossref fixture work",
        "PubMed fixture record",
        "MEDLINE fixture record",
    ]
    assert result.compatibility.library.surface is VersionedSurface.LIBRARY
    assert result.compatibility.output is not None
    assert result.compatibility.output.name == OutputFormat.JSONL.value
    assert result.manifest.record_count == OPEN_PROVIDER_FIXTURE_COUNT
    assert result.raw_records[0].provider is ProviderName.OPENALEX
    assert result.raw_records[0].content_digest.startswith("sha256:")
    assert result.raw_records[0].provider_version.surface is VersionedSurface.PROVIDER
    assert all(work.compatibility.provider is not None for work in result.works)


def test_pipeline_can_select_provider_registry_fixture_paths() -> None:
    request = ProviderPipelineRequest.from_registry_fixtures(
        (ProviderName.OPENALEX, ProviderName.CROSSREF, ProviderName.PUBMED),
        registry=DEFAULT_PROVIDER_REGISTRY,
        root=REPO,
        output_format=PipelineOutputFormat.CSL_JSON,
    )
    result = run_provider_pipeline(request)

    assert request.inputs[ProviderName.OPENALEX].name == "openalex.json"
    assert result.manifest.output_format is OutputFormat.CSL_JSON
    assert result.compatibility.output is not None
    assert result.compatibility.output.name == OutputFormat.CSL_JSON.value
    assert [work.source_provider for work in result.works] == [
        ProviderName.OPENALEX,
        ProviderName.CROSSREF,
        ProviderName.PUBMED,
    ]


def test_pipeline_rejects_unsupported_access_modes_and_missing_inputs(tmp_path: Path) -> None:
    with pytest.raises(PipelineError, match="credential-gated"):
        run_provider_pipeline(
            ProviderPipelineRequest(inputs={ProviderName.SCOPUS: FIXTURES / "scopus_export.csv"}),
        )

    with pytest.raises(PipelineError, match="export/import-only"):
        run_provider_pipeline(
            ProviderPipelineRequest(
                inputs={ProviderName.GOOGLE_SCHOLAR_EXPORT: FIXTURES / "google_scholar_export.bib"},
            ),
        )

    with pytest.raises(PipelineError, match="does not exist"):
        run_provider_pipeline(
            ProviderPipelineRequest(inputs={ProviderName.OPENALEX: tmp_path / "missing.json"}),
        )


def test_pipeline_rejects_invalid_provider_names_and_disabled_settings() -> None:
    with pytest.raises(ValidationError, match="provider"):
        ProviderPipelineRequest(inputs={"not-a-provider": FIXTURES / "openalex.json"})  # type: ignore[dict-item]

    settings = PyBibXSettings(providers=(ProviderSettings(provider=ProviderName.OPENALEX, enabled=False),))

    with pytest.raises(PipelineError, match="disabled"):
        run_provider_pipeline(
            ProviderPipelineRequest(inputs={ProviderName.OPENALEX: FIXTURES / "openalex.json"}),
            settings=settings,
        )


def test_pipeline_wraps_schema_failures(tmp_path: Path) -> None:
    invalid = tmp_path / "openalex.json"
    invalid.write_text('{"id":"https://openalex.org/Wbad","title":"Bad","doi":"not-a-doi"}', encoding="utf-8")

    with pytest.raises(PipelineError, match="failed to ingest openalex"):
        run_provider_pipeline(ProviderPipelineRequest(inputs={ProviderName.OPENALEX: invalid}))


def test_pipeline_exports_jsonl_and_csl_json(tmp_path: Path) -> None:
    result = run_provider_pipeline(
        ProviderPipelineRequest(
            inputs={
                ProviderName.OPENALEX: FIXTURES / "openalex.json",
                ProviderName.CROSSREF: FIXTURES / "crossref.json",
            },
        ),
    )

    jsonl_path = export_provider_pipeline_result(result, tmp_path / "works.jsonl", PipelineOutputFormat.JSONL)
    csl_path = export_provider_pipeline_result(result, tmp_path / "works.csl.json", PipelineOutputFormat.CSL_JSON)

    jsonl_rows = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines()]
    csl_items = json.loads(csl_path.read_text(encoding="utf-8"))

    assert [row["title"] for row in jsonl_rows] == ["OpenAlex fixture work", "Crossref fixture work"]
    assert [item["title"] for item in csl_items] == ["OpenAlex fixture work", "Crossref fixture work"]
    assert jsonl_rows[0]["compatibility"]["provider"]["name"] == "openalex"
    assert csl_items[0]["DOI"] == "10.1234/openalex.fixture"


def test_provider_pipeline_cli_runs_offline_fixture_exports(tmp_path: Path) -> None:
    output = tmp_path / "works.jsonl"

    completed = subprocess.run(  # noqa: S603 - fixed local Python executable and fixture paths.
        [
            sys.executable,
            "-m",
            "pybibx.pipeline",
            "--provider",
            "openalex",
            "--input",
            str(FIXTURES / "openalex.json"),
            "--provider",
            "crossref",
            "--input",
            str(FIXTURES / "crossref.json"),
            "--output-format",
            "jsonl",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert output.exists()
    assert "2 works" in completed.stdout
