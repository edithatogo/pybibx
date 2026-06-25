# Legacy Runtime Bridge Migration Notes

## Supported 6.0 To Legacy Workflow

The maintained provider pipeline should normalize provider records first. Feed the resulting
`Work` models into the isolated legacy bridge, then pass the pandas dataframe to the existing
`pbx_probe(data=..., db="scopus")` constructor.

```python
from pybibx import pbx_probe
from pybibx.legacy import works_to_legacy_dataframe
from pybibx.pipeline import ProviderPipelineRequest, run_provider_pipeline
from pybibx.schemas import ProviderName

result = run_provider_pipeline(
    ProviderPipelineRequest(inputs={ProviderName.OPENALEX: "openalex.json"}),
)
legacy_frame = works_to_legacy_dataframe(result.works)
probe = pbx_probe(data=legacy_frame, db="scopus")
```

The bridge emits deterministic columns for existing summary paths that depend on document
metadata, citation counts, authors, keywords, sources, institutions, and countries.

## Supported Legacy To 6.0 Workflow

Representative legacy dataframe exports can be converted back into maintained `Work` records and
export manifests:

```python
from pybibx.legacy import legacy_dataframe_to_export_manifest, legacy_dataframe_to_works
from pybibx.schemas import ProviderName

works = legacy_dataframe_to_works(legacy_export, source_provider=ProviderName.SCOPUS)
manifest = legacy_dataframe_to_export_manifest(legacy_export)
```

The reverse adapter recognizes common variants such as `Title`, `Authors`, `Year`, `DOI`,
`Citations`, `Document Type`, `Author Keywords`, `Institution`, and `Country`.

## Boundaries

Supported bridge-fed legacy analyses are:

- `author_counts`
- `citation_counts`
- `document_ids`
- `eda_report`
- `keyword_counts`
- `source_counts`

Unsupported paths fail through `LegacyBridgeError` or remain documented limitations:

- full-text RAG and semantic citation-intent extraction
- live provider ingestion
- GPU time-travel graph visualization
- any workflow that requires raw provider columns not represented in normalized `Work` records
