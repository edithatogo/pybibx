from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path  # noqa: TC003
from typing import Any, Self, cast

import jiter
import polars as pl
from pydantic import model_validator

from pybibx.providers import DEFAULT_PROVIDER_REGISTRY, ProviderAccessMode, ProviderSpec
from pybibx.schemas import Author, InputFormat, Institution, OntologyFacet, ProviderName, Work, WorkType
from pybibx.schemas.records import StrictSchemaModel, normalize_doi
from pybibx.versioning import CompatibilityProfile, VersionedSurface, VersionStamp


class IngestionError(ValueError):
    pass


class IngestionResult(StrictSchemaModel):
    provider: ProviderName
    source_path: Path
    input_format: InputFormat
    works: tuple[Work, ...]
    compatibility: CompatibilityProfile

    @model_validator(mode="after")
    def provider_matches_works(self) -> Self:
        mismatched = [work.work_id for work in self.works if work.source_provider is not self.provider]
        if mismatched:
            msg = f"normalized works do not match provider {self.provider}: {mismatched}"
            raise ValueError(msg)
        return self


def _provider_version(spec: ProviderSpec) -> VersionStamp:
    return VersionStamp(surface=VersionedSurface.PROVIDER, name=spec.provider.value, version=spec.version.version)


def _input_version(input_format: InputFormat) -> VersionStamp:
    return VersionStamp(surface=VersionedSurface.INPUT, name=input_format.value, version="1.0.0")


def _compatibility(spec: ProviderSpec, input_format: InputFormat) -> CompatibilityProfile:
    return CompatibilityProfile(provider=_provider_version(spec), input=_input_version(input_format))


def load_json_payload(path: Path) -> object:
    return jiter.from_json(path.read_bytes())


def scan_tabular(path: Path, *, separator: str = ",") -> pl.LazyFrame:
    return pl.scan_csv(path, separator=separator)


def _as_mapping(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        msg = "expected a JSON object"
        raise IngestionError(msg)
    return cast("dict[str, Any]", value)


def _text(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    if isinstance(value, list):
        return _text(cast("object", value[0])) if value else None
    return str(value)


def _year(value: object) -> int | None:
    text = _text(value)
    if text is None:
        return None
    match = re.search(r"\b(1\d{3}|2\d{3})\b", text)
    return int(match.group(1)) if match else None


def _doi(value: object) -> str | None:
    text = _text(value)
    if text is None:
        return None
    return normalize_doi(text)


class WorkDraft(StrictSchemaModel):
    work_id: str
    title: str
    doi: str | None = None
    publication_year: int | None = None
    authors: tuple[Author, ...] = ()
    institutions: tuple[Institution, ...] = ()
    citation_count: int = 0
    work_type: WorkType = WorkType.UNKNOWN


def _work(spec: ProviderSpec, input_format: InputFormat, draft: WorkDraft) -> Work:
    return Work(
        work_id=draft.work_id,
        title=draft.title,
        doi=draft.doi,
        publication_year=draft.publication_year,
        authors=draft.authors,
        institutions=draft.institutions,
        citation_count=draft.citation_count,
        source_provider=spec.provider,
        ontology=OntologyFacet(work_type=draft.work_type),
        compatibility=_compatibility(spec, input_format),
    )


JsonNormalizer = Callable[[ProviderSpec, InputFormat, dict[str, Any]], tuple[Work, ...]]


def _openalex_work(spec: ProviderSpec, input_format: InputFormat, payload: dict[str, Any]) -> tuple[Work, ...]:
    return (
        _work(
            spec,
            input_format,
            WorkDraft(
                work_id=str(payload["id"]),
                title=str(payload["title"]),
                doi=_doi(payload.get("doi")),
                publication_year=_year(payload.get("publication_year")),
                work_type=WorkType.JOURNAL_ARTICLE,
            ),
        ),
    )


def _crossref_work(spec: ProviderSpec, input_format: InputFormat, payload: dict[str, Any]) -> tuple[Work, ...]:
    message = _as_mapping(payload.get("message", {}))
    return (
        _work(
            spec,
            input_format,
            WorkDraft(
                work_id=f"crossref:{message.get('DOI')}",
                title=_text(message.get("title")) or "Untitled Crossref work",
                doi=_doi(message.get("DOI")),
                work_type=WorkType.JOURNAL_ARTICLE,
            ),
        ),
    )


def _pubmed_work(spec: ProviderSpec, input_format: InputFormat, payload: dict[str, Any]) -> tuple[Work, ...]:
    record = _pubmed_record(payload)
    return (
        _work(
            spec,
            input_format,
            WorkDraft(
                work_id=f"{spec.provider.value}:{record['id']}",
                title=str(record["title"]),
                publication_year=_year(record.get("year")),
            ),
        ),
    )


def _opencitations_work(spec: ProviderSpec, input_format: InputFormat, payload: dict[str, Any]) -> tuple[Work, ...]:
    return (
        _work(
            spec,
            input_format,
            WorkDraft(
                work_id=f"opencitations:{payload['cited']}",
                title=f"Cited work {payload['cited']}",
                doi=_doi(payload.get("cited")),
                publication_year=_year(payload.get("creation")),
            ),
        ),
    )


def _semantic_scholar_work(spec: ProviderSpec, input_format: InputFormat, payload: dict[str, Any]) -> tuple[Work, ...]:
    external_ids = _as_mapping(payload.get("externalIds", {}))
    return (
        _work(
            spec,
            input_format,
            WorkDraft(
                work_id=f"semantic_scholar:{payload['paperId']}",
                title=str(payload["title"]),
                doi=_doi(external_ids.get("DOI")),
                citation_count=int(payload.get("citationCount", 0)),
                work_type=WorkType.JOURNAL_ARTICLE,
            ),
        ),
    )


def _ror_work(spec: ProviderSpec, input_format: InputFormat, payload: dict[str, Any]) -> tuple[Work, ...]:
    country = _as_mapping(payload.get("country", {}))
    institution = Institution(
        display_name=str(payload["name"]),
        ror_id=str(payload["id"]),
        country_code=str(country.get("country_code", "ZZ")),
    )
    return (
        _work(
            spec,
            input_format,
            WorkDraft(
                work_id=f"ror:{payload['id']}",
                title=f"Organization profile: {institution.display_name}",
                institutions=(institution,),
            ),
        ),
    )


def _orcid_work(spec: ProviderSpec, input_format: InputFormat, payload: dict[str, Any]) -> tuple[Work, ...]:
    identifier = _as_mapping(payload.get("orcid-identifier", {}))
    person = _as_mapping(payload.get("person", {}))
    name_wrapper = _as_mapping(_as_mapping(person.get("name", {})).get("credit-name", {}))
    display_name = str(name_wrapper.get("value", identifier.get("path", "Unknown ORCID")))
    author = Author(display_name=display_name, orcid=_text(identifier.get("uri")))
    return (
        _work(
            spec,
            input_format,
            WorkDraft(
                work_id=f"orcid:{identifier.get('path')}",
                title=f"ORCID profile: {author.display_name}",
                authors=(author,),
            ),
        ),
    )


def _unpaywall_work(spec: ProviderSpec, input_format: InputFormat, payload: dict[str, Any]) -> tuple[Work, ...]:
    return (
        _work(
            spec,
            input_format,
            WorkDraft(
                work_id=f"unpaywall:{payload['doi']}",
                title=f"Open access record for {payload['doi']}",
                doi=_doi(payload.get("doi")),
            ),
        ),
    )


def _arxiv_work(spec: ProviderSpec, input_format: InputFormat, payload: dict[str, Any]) -> tuple[Work, ...]:
    return (
        _work(
            spec,
            input_format,
            WorkDraft(
                work_id=str(payload["id"]),
                title=str(payload["title"]),
                publication_year=_year(payload.get("published")),
                work_type=WorkType.PREPRINT,
            ),
        ),
    )


def _preprint_work(spec: ProviderSpec, input_format: InputFormat, payload: dict[str, Any]) -> tuple[Work, ...]:
    collection = payload.get("collection")
    if not isinstance(collection, list) or not collection:
        msg = f"{spec.provider.value} fixture must contain a non-empty collection"
        raise IngestionError(msg)
    first = _as_mapping(cast("object", collection[0]))
    return (
        _work(
            spec,
            input_format,
            WorkDraft(
                work_id=f"{spec.provider.value}:{first['doi']}",
                title=str(first["title"]),
                doi=_doi(first.get("doi")),
                work_type=WorkType.PREPRINT,
            ),
        ),
    )


JSON_NORMALIZERS: dict[ProviderName, JsonNormalizer] = {
    ProviderName.OPENALEX: _openalex_work,
    ProviderName.CROSSREF: _crossref_work,
    ProviderName.PUBMED: _pubmed_work,
    ProviderName.MEDLINE: _pubmed_work,
    ProviderName.OPENCITATIONS: _opencitations_work,
    ProviderName.SEMANTIC_SCHOLAR: _semantic_scholar_work,
    ProviderName.ROR: _ror_work,
    ProviderName.ORCID: _orcid_work,
    ProviderName.UNPAYWALL: _unpaywall_work,
    ProviderName.ARXIV: _arxiv_work,
    ProviderName.BIORXIV: _preprint_work,
    ProviderName.MEDRXIV: _preprint_work,
}


def _json_work(spec: ProviderSpec, input_format: InputFormat, payload: dict[str, Any]) -> tuple[Work, ...]:
    normalizer = JSON_NORMALIZERS.get(spec.provider)
    if normalizer is None:
        msg = f"unsupported JSON provider: {spec.provider}"
        raise IngestionError(msg)
    return normalizer(spec, input_format, payload)


def _pubmed_record(payload: dict[str, Any]) -> dict[str, object]:
    if "result" in payload:
        result = _as_mapping(payload["result"])
        uids = result.get("uids")
        if not isinstance(uids, list) or not uids:
            msg = "PubMed payload missing uids"
            raise IngestionError(msg)
        uid = str(cast("object", uids[0]))
        item = _as_mapping(cast("object", result[uid]))
        return {"id": item["uid"], "title": item["title"], "year": item.get("pubdate")}
    return {"id": payload["pmid"], "title": payload["title"], "year": payload.get("publication_year")}


def _tabular_works(
    spec: ProviderSpec,
    input_format: InputFormat,
    path: Path,
    *,
    separator: str = ",",
) -> tuple[Work, ...]:
    frame = scan_tabular(path, separator=separator).collect()
    works: list[Work] = []
    for row in frame.iter_rows(named=True):
        title = _text(row.get("Title") or row.get("TI")) or "Untitled export record"
        doi = _doi(row.get("DOI") or row.get("DI"))
        author_text = _text(row.get("Authors") or row.get("AU"))
        authors = (Author(display_name=author_text),) if author_text is not None else ()
        works.append(
            _work(
                spec,
                input_format,
                WorkDraft(
                    work_id=f"{spec.provider.value}:{doi or title}",
                    title=title,
                    doi=doi,
                    publication_year=_year(row.get("Year") or row.get("PY")),
                    authors=authors,
                ),
            ),
        )
    return tuple(works)


BIB_FIELD_RE = re.compile(r"^\s*(?P<key>[A-Za-z]+)\s*=\s*[{\"](?P<value>.*?)[}\"],?\s*$")


def _bibtex_work(spec: ProviderSpec, input_format: InputFormat, path: Path) -> tuple[Work, ...]:
    fields: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = BIB_FIELD_RE.match(line)
        if match:
            fields[match.group("key").lower()] = match.group("value").strip()
    author = fields.get("author")
    return (
        _work(
            spec,
            input_format,
            WorkDraft(
                work_id=f"{spec.provider.value}:{fields.get('doi', fields.get('title', 'unknown'))}",
                title=fields.get("title", "Untitled BibTeX record"),
                doi=_doi(fields.get("doi")),
                publication_year=_year(fields.get("year")),
                authors=(Author(display_name=author),) if author else (),
            ),
        ),
    )


def ingest_provider_file(
    path: Path,
    *,
    provider: ProviderName,
    input_format: InputFormat | None = None,
) -> IngestionResult:
    spec = DEFAULT_PROVIDER_REGISTRY.get(provider)
    resolved_format = input_format or _infer_input_format(path)
    if spec.access_mode is ProviderAccessMode.CREDENTIAL_GATED and resolved_format is InputFormat.JSON:
        msg = f"{provider.value} JSON/API ingestion requires configured credentials and a live adapter"
        raise IngestionError(msg)
    if resolved_format not in spec.supported_input_formats:
        msg = f"{provider.value} does not support {resolved_format.value} input"
        raise IngestionError(msg)

    if resolved_format is InputFormat.JSON:
        works = _json_work(spec, resolved_format, _as_mapping(load_json_payload(path)))
    elif resolved_format in {InputFormat.CSV, InputFormat.TSV}:
        separator = "\t" if resolved_format is InputFormat.TSV else ","
        works = _tabular_works(spec, resolved_format, path, separator=separator)
    elif resolved_format is InputFormat.BIBTEX:
        works = _bibtex_work(spec, resolved_format, path)
    else:
        msg = f"unsupported local ingestion format: {resolved_format.value}"
        raise IngestionError(msg)

    return IngestionResult(
        provider=provider,
        source_path=path,
        input_format=resolved_format,
        works=works,
        compatibility=_compatibility(spec, resolved_format),
    )


def _infer_input_format(path: Path) -> InputFormat:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return InputFormat.JSON
    if suffix == ".jsonl":
        return InputFormat.JSONL
    if suffix == ".csv":
        return InputFormat.CSV
    if suffix in {".txt", ".tsv"}:
        return InputFormat.TSV
    if suffix == ".bib":
        return InputFormat.BIBTEX
    msg = f"cannot infer input format for {path}"
    raise IngestionError(msg)
