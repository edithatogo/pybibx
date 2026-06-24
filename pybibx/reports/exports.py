from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, Self

from pydantic import Field, model_validator

from pybibx.schemas import Citation, EvidenceSet, ExportManifest, ExportProfile, OutputFormat, Work
from pybibx.schemas.records import StrictSchemaModel
from pybibx.versioning import CompatibilityProfile, VersionedSurface, VersionStamp, default_compatibility_profile

CITATION_SAFE_MARKDOWN_PROFILE = "citation-safe-markdown"
BIBLIB_MARKDOWN_PROFILE = "biblib-markdown"

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence


class ReportClaim(StrictSchemaModel):
    claim_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    evidence_set_ids: tuple[Annotated[str, Field(min_length=1)], ...] = Field(min_length=1)
    citation_ids: tuple[Annotated[str, Field(min_length=1)], ...] = Field(default_factory=tuple)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def references_are_unique(self) -> Self:
        if len(set(self.evidence_set_ids)) != len(self.evidence_set_ids):
            msg = "report claim evidence_set_ids must be unique"
            raise ValueError(msg)
        if len(set(self.citation_ids)) != len(self.citation_ids):
            msg = "report claim citation_ids must be unique"
            raise ValueError(msg)
        return self


class ReportSection(StrictSchemaModel):
    heading: str = Field(min_length=1)
    claim_ids: tuple[Annotated[str, Field(min_length=1)], ...] = Field(default_factory=tuple)
    body: str | None = None

    @model_validator(mode="after")
    def claim_ids_are_unique(self) -> Self:
        if len(set(self.claim_ids)) != len(self.claim_ids):
            msg = "report section claim_ids must be unique"
            raise ValueError(msg)
        return self


class CitationSafeReportContent(StrictSchemaModel):
    works: tuple[Work, ...] = Field(default_factory=tuple)
    citations: tuple[Citation, ...] = Field(default_factory=tuple)
    evidence_sets: tuple[EvidenceSet, ...] = Field(default_factory=tuple)
    claims: tuple[ReportClaim, ...] = Field(default_factory=tuple)
    sections: tuple[ReportSection, ...] = Field(default_factory=tuple)


class CitationSafeReport(StrictSchemaModel):
    report_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    works: tuple[Work, ...] = Field(default_factory=tuple)
    citations: tuple[Citation, ...] = Field(default_factory=tuple)
    evidence_sets: tuple[EvidenceSet, ...] = Field(default_factory=tuple)
    claims: tuple[ReportClaim, ...] = Field(default_factory=tuple)
    sections: tuple[ReportSection, ...] = Field(default_factory=tuple)
    manifest: ExportManifest
    compatibility: CompatibilityProfile = Field(default_factory=default_compatibility_profile)

    @model_validator(mode="after")
    def validate_report_links(self) -> Self:
        _raise_if_duplicate("report works", (item.work_id for item in self.works))
        _raise_if_duplicate("report evidence sets", (item.evidence_set_id for item in self.evidence_sets))
        _raise_if_duplicate("report citations", (_citation_key(item) for item in self.citations))
        _raise_if_duplicate("report claims", (item.claim_id for item in self.claims))
        evidence_set_ids = {item.evidence_set_id for item in self.evidence_sets}
        evidence_item_ids = {item.evidence_id for evidence_set in self.evidence_sets for item in evidence_set.items}
        citation_ids = {_citation_key(item) for item in self.citations}
        claim_ids = {item.claim_id for item in self.claims}
        unknown_evidence = sorted(
            evidence_id
            for claim in self.claims
            for evidence_id in claim.evidence_set_ids
            if evidence_id not in evidence_set_ids
        )
        if unknown_evidence:
            msg = f"report claims reference unknown evidence sets: {unknown_evidence}"
            raise ValueError(msg)
        unknown_citations = sorted(
            citation_id
            for claim in self.claims
            for citation_id in claim.citation_ids
            if citation_id not in citation_ids
        )
        if unknown_citations:
            msg = f"report claims reference unknown citations: {unknown_citations}"
            raise ValueError(msg)
        unknown_citation_evidence = sorted(
            evidence_id
            for citation in self.citations
            for evidence_id in citation.evidence_ids
            if evidence_id not in evidence_item_ids
        )
        if unknown_citation_evidence:
            msg = f"report citations reference unknown evidence items: {unknown_citation_evidence}"
            raise ValueError(msg)
        unknown_claims = sorted(
            claim_id for section in self.sections for claim_id in section.claim_ids if claim_id not in claim_ids
        )
        if unknown_claims:
            msg = f"report sections reference unknown claims: {unknown_claims}"
            raise ValueError(msg)
        if self.manifest.record_count != len(self.claims):
            msg = "report manifest record_count must match claim count"
            raise ValueError(msg)
        if set(self.manifest.evidence_set_ids) != evidence_set_ids:
            msg = "report manifest evidence_set_ids must match report evidence sets"
            raise ValueError(msg)
        return self


class MarkdownNoteBundle(StrictSchemaModel):
    profile: str = BIBLIB_MARKDOWN_PROFILE
    notes: dict[str, str] = Field(min_length=1)
    manifest: ExportManifest


class ReflexDashboardSpec(StrictSchemaModel):
    enabled: bool = False
    app_name: str = "pybibx_reports"
    route_prefix: str = "/reports"
    requires_optional_dependency: str = "reflex"


class CosmographExportSpec(StrictSchemaModel):
    enabled: bool = False
    graph_data_path: str | None = None
    time_field: str = "publication_year"
    node_id_field: str = "work_id"
    source_field: str = "source_work_id"
    target_field: str = "target_work_id"
    requires_frontend_package: str = "@cosmograph/cosmos"

    @model_validator(mode="after")
    def enabled_exports_require_path(self) -> Self:
        if self.enabled and self.graph_data_path is None:
            msg = "enabled Cosmograph exports require a graph data path"
            raise ValueError(msg)
        return self


class UiReportPlan(StrictSchemaModel):
    report_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    report_profile: str = CITATION_SAFE_MARKDOWN_PROFILE
    reflex: ReflexDashboardSpec = Field(default_factory=ReflexDashboardSpec)
    cosmograph: CosmographExportSpec = Field(default_factory=CosmographExportSpec)
    export_formats: tuple[OutputFormat, ...] = (
        OutputFormat.MARKDOWN,
        OutputFormat.CSL_JSON,
        OutputFormat.BIBTEX,
        OutputFormat.RIS,
    )
    require_evidence_for_claims: bool = True


def build_citation_safe_report(
    *,
    report_id: str,
    title: str,
    content: CitationSafeReportContent,
) -> CitationSafeReport:
    manifest = ExportManifest(
        export_id=report_id,
        export_profile=ExportProfile.EVIDENCE_REPORT,
        output_format=OutputFormat.MARKDOWN,
        record_count=len(content.claims),
        evidence_set_ids=tuple(item.evidence_set_id for item in content.evidence_sets),
    )
    return CitationSafeReport(
        report_id=report_id,
        title=title,
        works=content.works,
        citations=content.citations,
        evidence_sets=content.evidence_sets,
        claims=content.claims,
        sections=content.sections,
        manifest=manifest,
        compatibility=CompatibilityProfile(
            output=VersionStamp(surface=VersionedSurface.OUTPUT, name="citation-safe-report", version="1.0.0"),
        ),
    )


def render_citation_safe_markdown(report: CitationSafeReport) -> str:
    lines = [f"# {report.title}", "", f"Report ID: `{report.report_id}`", ""]
    lines.extend(_render_report_sections(report))
    lines.extend(["## Evidence", ""])
    evidence_sets = {item.evidence_set_id: item for item in report.evidence_sets}
    for evidence_id in sorted(evidence_sets):
        evidence_set = evidence_sets[evidence_id]
        locators = ", ".join(item.source_locator for item in evidence_set.items)
        lines.append(f"- [{evidence_id}] {evidence_set.claim_text}")
        lines.append(f"  Source: {locators}")
    lines.append("")
    return "\n".join(lines)


def export_csl_json(works: Sequence[Work]) -> list[dict[str, Any]]:
    return [_work_to_csl_item(work) for work in works]


def build_biblib_markdown_notes(works: Sequence[Work]) -> MarkdownNoteBundle:
    notes = {f"{_safe_note_name(work.work_id)}.md": _work_to_biblib_markdown(work) for work in works}
    if len(notes) != len(works):
        msg = "BibLib Markdown note filenames must be unique"
        raise ValueError(msg)
    manifest = ExportManifest(
        export_id="biblib-markdown",
        export_profile=ExportProfile.BIBLIB_MARKDOWN,
        output_format=OutputFormat.MARKDOWN,
        record_count=len(notes),
    )
    return MarkdownNoteBundle(notes=notes, manifest=manifest)


def build_default_ui_report_plan(*, report_id: str, title: str) -> UiReportPlan:
    return UiReportPlan(report_id=report_id, title=title)


def _render_report_sections(report: CitationSafeReport) -> list[str]:
    claims = {item.claim_id: item for item in report.claims}
    if not report.sections:
        return _render_claim_list("Claims", report.claims)
    lines: list[str] = []
    for section in report.sections:
        lines.extend([f"## {section.heading}", ""])
        if section.body is not None:
            lines.extend([section.body, ""])
        lines.extend(_render_claim(claims[claim_id]) for claim_id in section.claim_ids)
        lines.append("")
    return lines


def _render_claim_list(heading: str, claims: Sequence[ReportClaim]) -> list[str]:
    lines = [f"## {heading}", ""]
    lines.extend(_render_claim(claim) for claim in claims)
    lines.append("")
    return lines


def _render_claim(claim: ReportClaim) -> str:
    evidence_refs = " ".join(f"[{item}]" for item in claim.evidence_set_ids)
    return f"- {claim.text} {evidence_refs}"


def _work_to_csl_item(work: Work) -> dict[str, Any]:
    item: dict[str, Any] = {
        "id": work.work_id,
        "type": "article-journal",
        "title": work.title,
    }
    if work.doi is not None:
        item["DOI"] = work.doi
    if work.publication_year is not None:
        item["issued"] = {"date-parts": [[work.publication_year]]}
    if work.authors:
        item["author"] = [
            {"literal": author.display_name, **({"ORCID": author.orcid} if author.orcid is not None else {})}
            for author in work.authors
        ]
    return item


def _work_to_biblib_markdown(work: Work) -> str:
    frontmatter = [
        "---",
        f"work_id: {work.work_id}",
        f"title: {work.title}",
    ]
    if work.doi is not None:
        frontmatter.append(f"doi: {work.doi}")
    if work.publication_year is not None:
        frontmatter.append(f"year: {work.publication_year}")
    frontmatter.extend(["---", ""])
    lines = [*frontmatter, f"# {work.title}", ""]
    if work.authors:
        lines.extend(["## Authors", *[f"- {author.display_name}" for author in work.authors], ""])
    if work.concepts:
        lines.extend(["## Concepts", *[f"- {concept}" for concept in work.concepts], ""])
    return "\n".join(lines)


def _citation_key(citation: Citation) -> str:
    return f"{citation.source_work_id}->{citation.target_work_id}:{citation.intent.value}"


def _safe_note_name(value: str) -> str:
    return value.replace("/", "_").replace(":", "_")


def _raise_if_duplicate(label: str, values: Iterable[str]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    if duplicates:
        msg = f"{label} must be unique: {sorted(duplicates)}"
        raise ValueError(msg)
