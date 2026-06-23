"""Regression tests for maintained UI/report export contracts."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from pybibx.reports import (
    CitationSafeReportContent,
    CosmographExportSpec,
    MarkdownNoteBundle,
    ReportClaim,
    ReportSection,
    UiReportPlan,
    build_biblib_markdown_notes,
    build_citation_safe_report,
    build_default_ui_report_plan,
    export_csl_json,
    render_citation_safe_markdown,
)
from pybibx.schemas import Author, Citation, CitationIntent, EvidenceItem, EvidenceSet, ProviderName, Work


def _work() -> Work:
    return Work(
        work_id="W1",
        title="Evidence-grounded bibliometrics",
        doi="10.1234/EVIDENCE",
        publication_year=2026,
        publication_date=date(2026, 1, 1),
        authors=(Author(display_name="Ada Lovelace", orcid="0000-0002-1825-0097"),),
        concepts=("bibliometrics", "evidence"),
        source_provider=ProviderName.OPENALEX,
    )


def _evidence_set() -> EvidenceSet:
    evidence = EvidenceItem(
        evidence_id="ev1",
        source_provider=ProviderName.UNPAYWALL,
        source_locator="https://example.test/paper.pdf#page=4",
        quote="The method is contradicted by the later result.",
    )
    return EvidenceSet(
        evidence_set_id="set1",
        claim_text="The later paper contradicts the method.",
        items=(evidence,),
        supporting_item_ids=("ev1",),
    )


def test_report_claims_fail_closed_without_evidence_ids() -> None:
    with pytest.raises(ValidationError, match="evidence_set_ids"):
        ReportClaim(claim_id="c1", text="Unsupported synthesis", evidence_set_ids=())


def test_citation_safe_report_validates_claim_evidence_and_citations() -> None:
    work = _work()
    evidence_set = _evidence_set()
    citation = Citation(
        source_work_id="W1",
        target_work_id="W2",
        intent=CitationIntent.REFUTES,
        evidence_ids=("ev1",),
    )
    claim = ReportClaim(
        claim_id="claim1",
        text="The newer result refutes the older method.",
        evidence_set_ids=("set1",),
        citation_ids=("W1->W2:cito:refutes",),
        confidence=0.91,
    )

    report = build_citation_safe_report(
        report_id="report1",
        title="Citation-Safe Evidence Report",
        content=CitationSafeReportContent(
            works=(work,),
            citations=(citation,),
            evidence_sets=(evidence_set,),
            claims=(claim,),
            sections=(ReportSection(heading="Findings", claim_ids=("claim1",)),),
        ),
    )

    assert report.manifest.record_count == 1
    assert report.claims[0].evidence_set_ids == ("set1",)
    assert report.citations[0].intent is CitationIntent.REFUTES

    with pytest.raises(ValueError, match="unknown evidence sets"):
        build_citation_safe_report(
            report_id="bad-report",
            title="Bad Report",
            content=CitationSafeReportContent(
                works=(work,),
                evidence_sets=(evidence_set,),
                claims=(claim.model_copy(update={"evidence_set_ids": ("missing",)}),),
            ),
        )


def test_papersflow_style_markdown_renders_claims_with_evidence_references() -> None:
    report = build_citation_safe_report(
        report_id="report1",
        title="Citation-Safe Evidence Report",
        content=CitationSafeReportContent(
            works=(_work(),),
            evidence_sets=(_evidence_set(),),
            claims=(
                ReportClaim(
                    claim_id="claim1",
                    text="The later paper contradicts the method.",
                    evidence_set_ids=("set1",),
                ),
            ),
        ),
    )

    markdown = render_citation_safe_markdown(report)

    assert markdown.startswith("# Citation-Safe Evidence Report")
    assert "The later paper contradicts the method. [set1]" in markdown
    assert "## Evidence" in markdown
    assert "https://example.test/paper.pdf#page=4" in markdown


def test_csl_json_and_biblib_markdown_exports_are_deterministic() -> None:
    work = _work()

    csl = export_csl_json((work,))
    notes = build_biblib_markdown_notes((work,))

    assert csl == [
        {
            "id": "W1",
            "type": "article-journal",
            "title": "Evidence-grounded bibliometrics",
            "DOI": "10.1234/evidence",
            "issued": {"date-parts": [[2026]]},
            "author": [{"literal": "Ada Lovelace", "ORCID": "https://orcid.org/0000-0002-1825-0097"}],
        },
    ]
    assert isinstance(notes, MarkdownNoteBundle)
    assert notes.notes["W1.md"].startswith("---\nwork_id: W1\n")
    assert "doi: 10.1234/evidence" in notes.notes["W1.md"]
    assert "## Concepts\n- bibliometrics\n- evidence" in notes.notes["W1.md"]


def test_ui_report_plan_keeps_reflex_and_cosmograph_optional() -> None:
    plan = build_default_ui_report_plan(report_id="report1", title="Citation-Safe Evidence Report")

    assert isinstance(plan, UiReportPlan)
    assert plan.reflex.enabled is False
    assert plan.cosmograph.enabled is False
    assert plan.report_profile == "citation-safe-markdown"

    with pytest.raises(ValidationError, match="require a graph data path"):
        CosmographExportSpec(enabled=True)
