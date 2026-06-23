from __future__ import annotations

from enum import StrEnum


class ProviderName(StrEnum):
    OPENALEX = "openalex"
    CROSSREF = "crossref"
    PUBMED = "pubmed"
    MEDLINE = "medline"
    OPENCITATIONS = "opencitations"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    ROR = "ror"
    ORCID = "orcid"
    UNPAYWALL = "unpaywall"
    ARXIV = "arxiv"
    BIORXIV = "biorxiv"
    MEDRXIV = "medrxiv"
    SCOPUS = "scopus"
    WEB_OF_SCIENCE = "web_of_science"
    GOOGLE_SCHOLAR_EXPORT = "google_scholar_export"


class InputFormat(StrEnum):
    JSON = "json"
    JSONL = "jsonl"
    CSV = "csv"
    BIBTEX = "bibtex"
    RIS = "ris"
    CSL_JSON = "csl-json"
    XML = "xml"
    PDF = "pdf"
    MARKDOWN = "markdown"


class OutputFormat(StrEnum):
    PARQUET = "parquet"
    JSONL = "jsonl"
    CSL_JSON = "csl-json"
    BIBTEX = "bibtex"
    RIS = "ris"
    MARKDOWN = "markdown"
    GRAPHML = "graphml"


class WorkType(StrEnum):
    JOURNAL_ARTICLE = "fabio:JournalArticle"
    PREPRINT = "fabio:Preprint"
    BOOK = "fabio:Book"
    BOOK_CHAPTER = "fabio:BookChapter"
    CONFERENCE_PAPER = "fabio:ConferencePaper"
    DATASET = "fabio:Dataset"
    SOFTWARE = "fabio:ComputerProgram"
    REPORT = "fabio:ReportDocument"
    UNKNOWN = "fabio:Expression"


class PublicationStatus(StrEnum):
    DRAFT = "pso:draft"
    SUBMITTED = "pso:submittedVersion"
    ACCEPTED = "pso:acceptedVersion"
    PUBLISHED = "pso:publishedVersion"
    RETRACTED = "pso:retracted"


class CitationIntent(StrEnum):
    CITES = "cito:cites"
    SUPPORTS = "cito:supports"
    REFUTES = "cito:refutes"
    USES_METHOD_FROM = "cito:usesMethodFrom"
    PROVIDES_BACKGROUND = "cito:providesBackgroundFor"
    EXTENDS = "cito:extends"
    DISCUSSES = "cito:discusses"


class ExportProfile(StrEnum):
    NORMALIZED_RECORDS = "normalized-records"
    EVIDENCE_REPORT = "evidence-report"
    CITATION_GRAPH = "citation-graph"
    CSL_BIBLIOGRAPHY = "csl-bibliography"
    BIBLIB_MARKDOWN = "biblib-markdown"
    UI_REPORT_PLAN = "ui-report-plan"
