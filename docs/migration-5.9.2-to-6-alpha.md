# Migration Notes: PyBibX 5.9.2 To 6.0 Alpha

## Keep Existing Workflows

Existing imports remain valid:

```python
import pybibx

probe = pybibx.pbx_probe(file_bib="scopus.bib", db="scopus")
pybibx.web_app()
pybibx.web_stop()
```

The legacy runtime is still the supported path for mature notebook and web-app analyses.

## Add Maintained Schemas

Use the maintained records when building new ingestion or automation code:

```python
from pybibx.schemas import Author, Institution, Work

work = Work(
    work_id="W1",
    title="A typed bibliometric record",
    authors=(Author(display_name="Ada Lovelace"),),
    institutions=(Institution(display_name="Example University", country_code="AU"),),
)
```

## Configure Local Execution

```python
from pybibx.settings import PyBibXSettings

settings = PyBibXSettings()
```

Settings are Pydantic v2 models and are intended to keep hosted or credentialed services optional.

Do not treat `uv sync --all-extras --group dev` as a baseline migration command on Python 3.14. Use
`uv sync --group dev` first, then add feature-specific extras only when the relevant optional lane is needed.
These notes do not publish to PyPI or create a release tag.

## Use The Provider Pipeline

```python
from pybibx.pipeline import ProviderPipelineRequest, run_provider_pipeline
from pybibx.schemas import ProviderName

result = run_provider_pipeline(
    ProviderPipelineRequest(inputs={ProviderName.OPENALEX: "openalex.json"}),
)
```

Open providers can run from local fixtures and exports. Scopus and Web of Science live access stays credential-gated.

## Bridge Back To Legacy Analyses

```python
from pybibx import pbx_probe
from pybibx.legacy import works_to_legacy_dataframe

legacy_frame = works_to_legacy_dataframe(result.works)
probe = pbx_probe(data=legacy_frame, db="scopus")
```

The bridge supports deterministic metadata, author, institution, citation-count, and reference columns for representative legacy analyses. It does not make full-text RAG, semantic citation intent, or live provider ingestion part of the legacy runtime.

## Reports And Quality Lanes

```python
from pybibx.quality import build_default_quality_observability_plan
from pybibx.reports import build_default_ui_report_plan

quality_plan = build_default_quality_observability_plan()
report_plan = build_default_ui_report_plan(report_id="alpha-report", title="Alpha report")
```

These are planning contracts for early adopters. Heavy optional tools remain optional extras.
