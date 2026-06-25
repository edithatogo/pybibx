"""Bridge maintained PyBibX records to the legacy pandas runtime."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from pybibx.schemas import (
    Author,
    Citation,
    ExportManifest,
    ExportProfile,
    InputFormat,
    Institution,
    OntologyFacet,
    OutputFormat,
    ProviderName,
    Work,
    WorkType,
)
from pybibx.versioning import (
    CompatibilityProfile,
    VersionedSurface,
    VersionStamp,
    default_compatibility_profile,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

UNKNOWN = "UNKNOWN"
UNKNOWN_YEAR = "0"
UNKNOWN_COUNTRY_CODE = "ZZ"

LEGACY_DATAFRAME_COLUMNS: tuple[str, ...] = (
    "source",
    "document_type",
    "author",
    "title",
    "year",
    "journal",
    "abbrev_source_title",
    "doi",
    "note",
    "abstract",
    "author_keywords",
    "keywords",
    "references",
    "affiliation",
    "affiliation_",
    "correspondence_address1",
    "language",
    "country",
    "institution",
    "legacy_work_id",
    "pybibx_work_id",
    "pybibx_library_version",
    "pybibx_schema_version",
    "pybibx_provider_version",
    "pybibx_input_version",
    "pybibx_output_version",
)

SUPPORTED_LEGACY_ANALYSES: tuple[str, ...] = (
    "author_counts",
    "citation_counts",
    "document_ids",
    "eda_report",
    "keyword_counts",
    "source_counts",
)
UNSUPPORTED_LEGACY_ANALYSES: tuple[str, ...] = (
    "full_text_rag",
    "semantic_citation_intent",
    "live_provider_ingestion",
    "gpu_time_travel_graph",
)

WORK_TYPE_TO_LEGACY_DOCUMENT_TYPE: Mapping[WorkType, str] = {
    WorkType.BOOK: "Book",
    WorkType.BOOK_CHAPTER: "Book Chapter",
    WorkType.CONFERENCE_PAPER: "Conference Paper",
    WorkType.DATASET: "Dataset",
    WorkType.JOURNAL_ARTICLE: "Article",
    WorkType.PREPRINT: "Preprint",
    WorkType.REPORT: "Report",
    WorkType.SOFTWARE: "Software",
    WorkType.UNKNOWN: UNKNOWN,
}

LEGACY_DOCUMENT_TYPE_TO_WORK_TYPE: Mapping[str, WorkType] = {
    "article": WorkType.JOURNAL_ARTICLE,
    "book": WorkType.BOOK,
    "book chapter": WorkType.BOOK_CHAPTER,
    "conference paper": WorkType.CONFERENCE_PAPER,
    "dataset": WorkType.DATASET,
    "preprint": WorkType.PREPRINT,
    "report": WorkType.REPORT,
    "software": WorkType.SOFTWARE,
}

TITLE_ALIASES = ("title", "ti")
AUTHOR_ALIASES = ("author", "authors", "au")
YEAR_ALIASES = ("year", "publication_year", "py")
DOI_ALIASES = ("doi", "di")
DOCUMENT_TYPE_ALIASES = ("document_type", "type", "dt")
JOURNAL_ALIASES = ("journal", "abbrev_source_title", "source", "so", "source title")
NOTE_ALIASES = ("note", "cited_by", "citation_count", "citations", "times cited")
KEYWORD_ALIASES = ("author_keywords", "keywords", "kw")
INSTITUTION_ALIASES = ("institution", "institutions", "affiliation", "affiliations")
COUNTRY_ALIASES = ("country", "country_code")
WORK_ID_ALIASES = ("pybibx_work_id", "legacy_work_id", "work_id", "id")


class LegacyBridgeError(ValueError):
    """Raised when legacy bridge conversion cannot be completed safely."""


class LegacyBridgeDiagnostic(BaseModel):
    """Lossiness metadata from a legacy bridge conversion."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    row_index: int
    field: str
    message: str = Field(min_length=1)


def works_to_legacy_dataframe(
    works: Sequence[Work],
    *,
    citations: Sequence[Citation] = (),
    source: str = "pybibx6",
) -> pd.DataFrame:
    """Convert maintained `Work` records to the minimal legacy `pbx_probe` dataframe shape."""
    references_by_source = _legacy_references_by_source(citations)
    rows = [
        _work_to_legacy_row(
            work,
            references=_references_for_work(work, references_by_source),
            source=source,
        )
        for work in works
    ]
    return pd.DataFrame(rows, columns=LEGACY_DATAFRAME_COLUMNS)


def legacy_dataframe_to_works(frame: pd.DataFrame, *, source_provider: ProviderName | None = None) -> tuple[Work, ...]:
    """Convert a representative legacy dataframe/export into maintained `Work` records."""
    normalized_columns = _normalized_column_lookup(frame.columns.tolist())
    if _first_column(normalized_columns, TITLE_ALIASES) is None:
        msg = "legacy dataframe must include a title column"
        raise LegacyBridgeError(msg)

    works: list[Work] = []
    for row_index, row in enumerate(frame.to_dict(orient="records")):
        values = {str(column): value for column, value in row.items()}
        try:
            works.append(_legacy_row_to_work(row_index, values, normalized_columns, source_provider))
        except (TypeError, ValueError, ValidationError) as exc:
            msg = f"failed to convert legacy row {row_index}: {exc}"
            raise LegacyBridgeError(msg) from exc
    return tuple(works)


def legacy_dataframe_to_citations(frame: pd.DataFrame) -> tuple[Citation, ...]:
    """Convert legacy `references` columns into maintained citation edges."""
    normalized_columns = _normalized_column_lookup(frame.columns.tolist())
    reference_column = _first_column(normalized_columns, ("references", "cited_references", "cr"))
    if reference_column is None:
        msg = "legacy dataframe must include a references column for citation conversion"
        raise LegacyBridgeError(msg)

    doi_column = _first_column(normalized_columns, DOI_ALIASES)
    work_id_column = _first_column(normalized_columns, WORK_ID_ALIASES)
    citations: list[Citation] = []
    for row_index, row in enumerate(frame.to_dict(orient="records")):
        values = {str(column): value for column, value in row.items()}
        source_doi = _valid_optional_doi(_optional_cell(values, doi_column))
        source_work_id = _source_work_id(row_index, values, work_id_column, source_doi)
        for target in _split_semicolon_values(_optional_cell(values, reference_column)):
            try:
                citations.append(
                    Citation(
                        source_work_id=source_work_id,
                        target_work_id=target,
                        source_doi=source_doi,
                        target_doi=_valid_optional_doi(target),
                        compatibility=_bridge_compatibility(input_format=InputFormat.CSV),
                    ),
                )
            except (TypeError, ValueError, ValidationError) as exc:
                msg = f"failed to convert legacy citation in row {row_index}: {exc}"
                raise LegacyBridgeError(msg) from exc
    return tuple(citations)


def legacy_dataframe_to_export_manifest(
    frame: pd.DataFrame,
    *,
    export_id: str = "legacy-runtime-bridge",
    output_format: OutputFormat = OutputFormat.JSONL,
) -> ExportManifest:
    """Create a maintained export manifest for a legacy dataframe/export."""
    return ExportManifest(
        export_id=export_id,
        export_profile=ExportProfile.NORMALIZED_RECORDS,
        input_format=InputFormat.CSV,
        output_format=output_format,
        record_count=len(frame),
        compatibility=_bridge_compatibility(input_format=InputFormat.CSV, output_format=output_format),
    )


def require_supported_legacy_analysis(analysis_name: str) -> None:
    """Fail closed for unsupported legacy analysis paths."""
    normalized = analysis_name.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in SUPPORTED_LEGACY_ANALYSES:
        return
    msg = (
        f"legacy analysis {analysis_name!r} is not supported by normalized-record bridge inputs. "
        f"Supported analyses: {', '.join(SUPPORTED_LEGACY_ANALYSES)}."
    )
    raise LegacyBridgeError(msg)


def _work_to_legacy_row(work: Work, *, references: str, source: str) -> dict[str, str]:
    compatibility = work.compatibility
    author_value = _join_nonempty((author.display_name for author in work.authors), separator=" and ")
    institution_value = _join_nonempty(institution.display_name for institution in work.institutions)
    country_value = _join_nonempty(institution.country_code for institution in work.institutions)
    keyword_value = _join_nonempty(work.concepts)
    sdg_value = _join_nonempty(work.sustainable_development_goals)
    provider_name = work.source_provider.value if work.source_provider is not None else source
    document_type = WORK_TYPE_TO_LEGACY_DOCUMENT_TYPE.get(work.ontology.work_type, UNKNOWN)

    return {
        "source": provider_name,
        "document_type": document_type,
        "author": author_value,
        "title": work.title,
        "year": str(work.publication_year) if work.publication_year is not None else UNKNOWN_YEAR,
        "journal": UNKNOWN,
        "abbrev_source_title": UNKNOWN,
        "doi": work.doi or UNKNOWN,
        "note": f"Cited by: {work.citation_count}",
        "abstract": UNKNOWN,
        "author_keywords": keyword_value,
        "keywords": sdg_value,
        "references": references,
        "affiliation": institution_value,
        "affiliation_": institution_value,
        "correspondence_address1": institution_value,
        "language": "English",
        "country": country_value,
        "institution": institution_value,
        "legacy_work_id": work.doi or work.work_id,
        "pybibx_work_id": work.work_id,
        "pybibx_library_version": compatibility.library.version,
        "pybibx_schema_version": compatibility.schema_profile.version,
        "pybibx_provider_version": compatibility.provider.version if compatibility.provider is not None else "",
        "pybibx_input_version": compatibility.input.version if compatibility.input is not None else "",
        "pybibx_output_version": compatibility.output.version if compatibility.output is not None else "",
    }


def _legacy_row_to_work(
    row_index: int,
    values: Mapping[str, object],
    normalized_columns: Mapping[str, str],
    source_provider: ProviderName | None,
) -> Work:
    title = _required_string(values, normalized_columns, TITLE_ALIASES, field_name="title")
    author_value = _optional_string(values, normalized_columns, AUTHOR_ALIASES)
    institution_value = _optional_string(values, normalized_columns, INSTITUTION_ALIASES)
    country_value = _optional_string(values, normalized_columns, COUNTRY_ALIASES)
    document_type_value = _optional_string(values, normalized_columns, DOCUMENT_TYPE_ALIASES)
    keyword_value = _optional_string(values, normalized_columns, KEYWORD_ALIASES)
    doi = _optional_string(values, normalized_columns, DOI_ALIASES)
    work_id = _optional_string(values, normalized_columns, WORK_ID_ALIASES) or doi or f"legacy:{row_index}"

    return Work(
        work_id=work_id,
        title=title,
        doi=None if _is_unknown(doi) else doi,
        publication_year=_parse_year(_optional_string(values, normalized_columns, YEAR_ALIASES)),
        authors=tuple(Author(display_name=name, raw_name=name) for name in _split_people(author_value)),
        institutions=tuple(_institutions_from_legacy(institution_value, country_value)),
        concepts=tuple(_split_semicolon_values(keyword_value)),
        citation_count=_parse_citation_count(_optional_string(values, normalized_columns, NOTE_ALIASES)),
        source_provider=source_provider,
        ontology=OntologyFacet(work_type=_legacy_work_type(document_type_value)),
        compatibility=_bridge_compatibility(input_format=InputFormat.CSV),
    )


def _bridge_compatibility(
    *,
    input_format: InputFormat,
    output_format: OutputFormat | None = None,
) -> CompatibilityProfile:
    return default_compatibility_profile().model_copy(
        update={
            "input": VersionStamp(surface=VersionedSurface.INPUT, name=input_format.value, version="legacy-runtime"),
            "output": (
                VersionStamp(surface=VersionedSurface.OUTPUT, name=output_format.value, version="legacy-runtime")
                if output_format is not None
                else None
            ),
        },
    )


def _legacy_references_by_source(citations: Sequence[Citation]) -> dict[str, list[str]]:
    references_by_source: dict[str, list[str]] = {}
    for citation in citations:
        reference = citation.target_doi or citation.target_work_id
        for source_key in (citation.source_work_id, citation.source_doi):
            if source_key is None:
                continue
            references_by_source.setdefault(source_key, []).append(reference)
    return references_by_source


def _references_for_work(work: Work, references_by_source: Mapping[str, list[str]]) -> str:
    references = references_by_source.get(work.work_id, [])
    if work.doi is not None:
        references = [*references, *references_by_source.get(work.doi, [])]
    return _join_nonempty(dict.fromkeys(references))


def _normalized_column_lookup(columns: list[object]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for column in columns:
        original = str(column)
        lookup.setdefault(_normalize_column_name(original), original)
    return lookup


def _normalize_column_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def _first_column(normalized_columns: Mapping[str, str], aliases: Sequence[str]) -> str | None:
    for alias in aliases:
        column = normalized_columns.get(_normalize_column_name(alias))
        if column is not None:
            return column
    return None


def _optional_string(
    values: Mapping[str, object],
    normalized_columns: Mapping[str, str],
    aliases: Sequence[str],
) -> str | None:
    column = _first_column(normalized_columns, aliases)
    if column is None:
        return None
    value = values[column]
    text = str(value).strip()
    return text or None


def _optional_cell(values: Mapping[str, object], column: str | None) -> str | None:
    if column is None:
        return None
    value = values[column]
    text = str(value).strip()
    return text or None


def _required_string(
    values: Mapping[str, object],
    normalized_columns: Mapping[str, str],
    aliases: Sequence[str],
    *,
    field_name: str,
) -> str:
    value = _optional_string(values, normalized_columns, aliases)
    if value is None or _is_unknown(value):
        msg = f"legacy row is missing required {field_name}"
        raise LegacyBridgeError(msg)
    return value


def _is_unknown(value: str | None) -> bool:
    return value is None or value.strip().lower() in {"", "unknown", "none", "nan", "null"}


def _valid_optional_doi(value: str | None) -> str | None:
    if _is_unknown(value):
        return None
    try:
        return Work(work_id="doi-validator", title="DOI validator", doi=value).doi
    except ValidationError:
        return None


def _source_work_id(
    row_index: int,
    values: Mapping[str, object],
    work_id_column: str | None,
    source_doi: str | None,
) -> str:
    work_id = _optional_cell(values, work_id_column)
    if work_id is not None and not _is_unknown(work_id):
        return work_id
    return source_doi or f"legacy:{row_index}"


def _join_nonempty(values: Iterable[str], *, separator: str = "; ") -> str:
    text_values = [value.strip() for value in values if value.strip()]
    return separator.join(text_values) if text_values else UNKNOWN


def _split_people(value: str | None) -> tuple[str, ...]:
    if _is_unknown(value):
        return ()
    if value is None:
        return ()
    chunks = re.split(r"\s+and\s+|;", value)
    return tuple(chunk.strip() for chunk in chunks if chunk.strip() and not _is_unknown(chunk))


def _split_semicolon_values(value: str | None) -> tuple[str, ...]:
    if _is_unknown(value):
        return ()
    if value is None:
        return ()
    return tuple(chunk.strip() for chunk in value.split(";") if chunk.strip() and not _is_unknown(chunk))


def _institutions_from_legacy(institution_value: str | None, country_value: str | None) -> tuple[Institution, ...]:
    institutions = _split_semicolon_values(institution_value)
    if not institutions:
        return ()
    countries = _split_semicolon_values(country_value)
    country = countries[0].upper() if countries and re.fullmatch(r"[A-Za-z]{2}", countries[0]) else UNKNOWN_COUNTRY_CODE
    return tuple(Institution(display_name=institution, country_code=country) for institution in institutions)


def _parse_year(value: str | None) -> int | None:
    if _is_unknown(value):
        return None
    if value is None:
        return None
    match = re.search(r"\d{4}", value)
    return int(match.group(0)) if match else None


def _parse_citation_count(value: str | None) -> int:
    if _is_unknown(value):
        return 0
    if value is None:
        return 0
    match = re.search(r"\d+", value)
    return int(match.group(0)) if match else 0


def _legacy_work_type(value: str | None) -> WorkType:
    if _is_unknown(value):
        return WorkType.UNKNOWN
    if value is None:
        return WorkType.UNKNOWN
    return LEGACY_DOCUMENT_TYPE_TO_WORK_TYPE.get(value.strip().lower(), WorkType.UNKNOWN)
