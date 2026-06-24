"""Regression tests for maintained UI/report export contracts."""

from __future__ import annotations

import subprocess
import sys
import textwrap
from datetime import date

import pytest
from pydantic import ValidationError

from pybibx.reports import (
    CitationSafeReport,
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
from pybibx.schemas import (
    Author,
    Citation,
    CitationIntent,
    EvidenceItem,
    EvidenceSet,
    ExportManifest,
    ExportProfile,
    OutputFormat,
    ProviderName,
    Work,
)


def test_reports_package_imports_without_optional_ui_dependencies() -> None:
    code = textwrap.dedent(
        """
        import sys
        from importlib.abc import MetaPathFinder

        blocked = {
            'reflex', 'cosmograph', 'pandas', 'numpy', 'scipy', 'sklearn',
            'torch', 'transformers', 'gensim', 'flask', 'pybibx.base',
            'pybibx.base.pbx',
        }

        class Blocker(MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                if any(fullname == item or fullname.startswith(f'{item}.') for item in blocked):
                    raise AssertionError(fullname)
                return None

        sys.meta_path.insert(0, Blocker())
        import pybibx.reports as reports

        assert reports.UiReportPlan(report_id='r1', title='Report').report_profile == 'citation-safe-markdown'
        loaded = blocked.intersection(sys.modules)
        assert not loaded, sorted(loaded)
        """,
    )

    subprocess.run([sys.executable, "-c", code], check=True)  # noqa: S603


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

    with pytest.raises(ValidationError, match="string_too_short"):
        ReportClaim(claim_id="c1", text="Unsupported synthesis", evidence_set_ids=("",))

    with pytest.raises(ValidationError, match="must be unique"):
        ReportClaim(claim_id="c1", text="Unsupported synthesis", evidence_set_ids=("set1", "set1"))

    with pytest.raises(ValidationError, match="must be unique"):
        ReportClaim(
            claim_id="c1",
            text="Unsupported synthesis",
            evidence_set_ids=("set1",),
            citation_ids=("W1->W2:cito:cites", "W1->W2:cito:cites"),
        )


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

    with pytest.raises(ValueError, match="unknown citations"):
        build_citation_safe_report(
            report_id="bad-citation-report",
            title="Bad Citation Report",
            content=CitationSafeReportContent(
                works=(work,),
                citations=(citation,),
                evidence_sets=(evidence_set,),
                claims=(claim.model_copy(update={"citation_ids": ("W1->W3:cito:refutes",)}),),
            ),
        )

    with pytest.raises(ValueError, match="unknown evidence items"):
        build_citation_safe_report(
            report_id="bad-citation-evidence-report",
            title="Bad Citation Evidence Report",
            content=CitationSafeReportContent(
                works=(work,),
                citations=(citation.model_copy(update={"evidence_ids": ("missing-ev",)}),),
                evidence_sets=(evidence_set,),
                claims=(claim,),
            ),
        )

    with pytest.raises(ValueError, match="unknown claims"):
        build_citation_safe_report(
            report_id="bad-section-report",
            title="Bad Section Report",
            content=CitationSafeReportContent(
                works=(work,),
                evidence_sets=(evidence_set,),
                claims=(claim.model_copy(update={"citation_ids": ()}),),
                sections=(ReportSection(heading="Findings", claim_ids=("missing",)),),
            ),
        )

    with pytest.raises(ValueError, match="report claims must be unique"):
        build_citation_safe_report(
            report_id="duplicate-claim-report",
            title="Duplicate Claim Report",
            content=CitationSafeReportContent(
                works=(work,),
                evidence_sets=(evidence_set,),
                claims=(claim.model_copy(update={"citation_ids": ()}), claim.model_copy(update={"citation_ids": ()})),
            ),
        )

    report_manifest = ExportManifest(
        export_id="manual-report",
        export_profile=ExportProfile.EVIDENCE_REPORT,
        output_format=OutputFormat.MARKDOWN,
        record_count=1,
        evidence_set_ids=("missing",),
    )
    with pytest.raises(ValueError, match="manifest evidence_set_ids"):
        CitationSafeReport(
            report_id="manual-report",
            title="Manual Report",
            evidence_sets=(evidence_set,),
            claims=(claim.model_copy(update={"citation_ids": ()}),),
            manifest=report_manifest,
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
    assert notes.manifest.export_profile is ExportProfile.BIBLIB_MARKDOWN
    assert notes.manifest.output_format is OutputFormat.MARKDOWN
    assert notes.notes["W1.md"].startswith("---\nwork_id: W1\n")
    assert "doi: 10.1234/evidence" in notes.notes["W1.md"]
    assert "## Concepts\n- bibliometrics\n- evidence" in notes.notes["W1.md"]

    first = work.model_copy(update={"work_id": "A/B"})
    second = work.model_copy(update={"work_id": "A:B"})
    with pytest.raises(ValueError, match="filenames must be unique"):
        build_biblib_markdown_notes((first, second))


def test_ui_report_plan_keeps_reflex_and_cosmograph_optional() -> None:
    plan = build_default_ui_report_plan(report_id="report1", title="Citation-Safe Evidence Report")

    assert isinstance(plan, UiReportPlan)
    assert plan.reflex.enabled is False
    assert plan.cosmograph.enabled is False
    assert plan.report_profile == "citation-safe-markdown"

    with pytest.raises(ValidationError, match="require a graph data path"):
        CosmographExportSpec(enabled=True)

    with pytest.raises(ValidationError, match="must be unique"):
        ReportSection(heading="Findings", claim_ids=("claim1", "claim1"))
