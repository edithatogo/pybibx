from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from enum import StrEnum
from hashlib import sha256
from typing import Protocol, Self, cast
from urllib.parse import urlparse

from pydantic import Field, field_validator, model_validator

from pybibx.schemas import EvidenceItem, EvidenceSet, ProviderName
from pybibx.schemas.records import StrictSchemaModel, normalize_doi
from pybibx.versioning import VersionedSurface, VersionStamp

DEFAULT_CHUNK_CHARS = 1_200
MIN_CHUNK_CHARS = 200
ARXIV_ABS_PREFIX = "http://arxiv.org/abs/"
ARXIV_PDF_PREFIX = "https://arxiv.org/pdf/"
PREPRINT_PDF_TEMPLATE = "https://www.{server}.org/content/{doi}v1.full.pdf"
LEGAL_FULL_TEXT_SCHEME = "https"
ARXIV_HOST = "arxiv.org"
ARXIV_ID_RE = re.compile(r"^(?:\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?$", re.IGNORECASE)
SOURCE_FINGERPRINT_LENGTH = 12


class FullTextSourceKind(StrEnum):
    UNPAYWALL = "unpaywall"
    ARXIV = "arxiv"
    BIORXIV = "biorxiv"
    MEDRXIV = "medrxiv"
    USER_PROVIDED = "user-provided"


class ParserBackend(StrEnum):
    DOCLING = "docling"
    PDFMUX = "pdfmux"


class EmbeddingBackend(StrEnum):
    FASTEMBED = "fastembed"


class VectorStoreBackend(StrEnum):
    LANCEDB = "lancedb"


class FullTextRoute(StrictSchemaModel):
    route_id: str = Field(min_length=1)
    work_id: str = Field(min_length=1)
    source_kind: FullTextSourceKind
    provider: ProviderName
    url: str = Field(min_length=1)
    doi: str | None = None
    license: str | None = None
    is_legal: bool
    requires_credentials: bool = False
    terms_note: str = Field(min_length=1)
    source_version: VersionStamp

    @field_validator("doi")
    @classmethod
    def validate_doi(cls, value: str | None) -> str | None:
        return normalize_doi(value)


class PdfParseCandidate(StrictSchemaModel):
    route: FullTextRoute
    parser_backend: ParserBackend
    parser_version: str | None = None

    @model_validator(mode="after")
    def route_is_local_parseable(self) -> Self:
        if not self.route.is_legal or self.route.requires_credentials:
            msg = "PDF parse candidates must use legal credential-free routes"
            raise ValueError(msg)
        return self


class ParserEvaluation(StrictSchemaModel):
    backend: ParserBackend
    local_execution: bool
    parses_tables: bool
    parses_formulas: bool
    handles_multi_column: bool
    requires_credentials: bool = False
    terms_review_required: bool = False
    recommendation: str = Field(min_length=1)


class ParsedDocument(StrictSchemaModel):
    candidate: PdfParseCandidate
    markdown: str = Field(min_length=1)
    source_locator: str = Field(min_length=1)
    page_count: int | None = Field(default=None, ge=1)
    warnings: tuple[str, ...] = Field(default_factory=tuple)


class PdfParserAdapter(Protocol):
    backend: ParserBackend

    def parse(self, candidate: PdfParseCandidate) -> ParsedDocument: ...


class TextChunk(StrictSchemaModel):
    chunk_id: str = Field(min_length=1)
    work_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    source_locator: str = Field(min_length=1)
    section_path: tuple[str, ...] = Field(default_factory=tuple)
    start_char: int = Field(ge=0)
    end_char: int = Field(gt=0)

    @model_validator(mode="after")
    def end_after_start(self) -> Self:
        if self.end_char <= self.start_char:
            msg = "end_char must be greater than start_char"
            raise ValueError(msg)
        return self


class EmbeddingRecord(StrictSchemaModel):
    chunk_id: str = Field(min_length=1)
    backend: EmbeddingBackend = EmbeddingBackend.FASTEMBED
    model_name: str = Field(min_length=1)
    vector: tuple[float, ...] = Field(min_length=1)


class VectorStoreRecord(StrictSchemaModel):
    chunk: TextChunk
    embedding: EmbeddingRecord
    backend: VectorStoreBackend = VectorStoreBackend.LANCEDB

    @model_validator(mode="after")
    def embedding_matches_chunk(self) -> Self:
        if self.chunk.chunk_id != self.embedding.chunk_id:
            msg = "embedding chunk_id must match chunk chunk_id"
            raise ValueError(msg)
        return self

    def to_lancedb_record(self) -> dict[str, object]:
        return {
            "id": self.chunk.chunk_id,
            "chunk_id": self.chunk.chunk_id,
            "work_id": self.chunk.work_id,
            "text": self.chunk.text,
            "source_locator": self.chunk.source_locator,
            "section_path": list(self.chunk.section_path),
            "start_char": self.chunk.start_char,
            "end_char": self.chunk.end_char,
            "vector": list(self.embedding.vector),
            "embedding_model": self.embedding.model_name,
            "embedding_backend": self.embedding.backend.value,
            "vector_backend": self.backend.value,
        }


class GroundedExtraction(StrictSchemaModel):
    extraction_id: str = Field(min_length=1)
    work_id: str = Field(min_length=1)
    claim_text: str = Field(min_length=1)
    evidence_set: EvidenceSet
    extraction_backend: str = Field(min_length=1)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def claim_matches_evidence(self) -> Self:
        if self.evidence_set.claim_text != self.claim_text:
            msg = "evidence_set claim_text must match extraction claim_text"
            raise ValueError(msg)
        for item in self.evidence_set.items:
            if item.quote is None or item.quote.strip() == "":
                msg = "grounded extraction evidence items must include concrete chunk quotes"
                raise ValueError(msg)
            if not item.evidence_id.startswith(f"{self.work_id}:source:"):
                msg = "grounded extraction evidence chunk IDs must match extraction work_id"
                raise ValueError(msg)
        return self


class RagPipelinePlan(StrictSchemaModel):
    routes: tuple[FullTextRoute, ...]
    parser_evaluations: tuple[ParserEvaluation, ...]
    embedding_backend: EmbeddingBackend = EmbeddingBackend.FASTEMBED
    vector_backend: VectorStoreBackend = VectorStoreBackend.LANCEDB
    evidence_required: bool = True

    @model_validator(mode="after")
    def evidence_requires_usable_routes(self) -> Self:
        if self.evidence_required and not self.routes:
            msg = "evidence-required RAG plans must include at least one legal credential-free route"
            raise ValueError(msg)
        return self


def route_unpaywall_full_text(payload: Mapping[str, object], *, work_id: str | None = None) -> FullTextRoute | None:
    if payload.get("is_oa") is not True:
        return None
    doi = _text(payload.get("doi"))
    if doi is None:
        return None
    location = _mapping(payload.get("best_oa_location"))
    if location is None:
        return None
    url = _legal_pdf_url(_text(location.get("url_for_pdf")))
    if url is None:
        return None
    normalized_doi = _required_doi(doi)
    return FullTextRoute(
        route_id=f"unpaywall:{normalized_doi}",
        work_id=work_id or f"doi:{normalized_doi}",
        source_kind=FullTextSourceKind.UNPAYWALL,
        provider=ProviderName.UNPAYWALL,
        url=url,
        doi=normalized_doi,
        license=_text(location.get("license")),
        is_legal=True,
        terms_note="Routed through Unpaywall open-access metadata; fetch only the legal OA URL returned.",
        source_version=VersionStamp(surface=VersionedSurface.PROVIDER, name=ProviderName.UNPAYWALL.value, version="v2"),
    )


def route_preprint_full_text(provider: ProviderName, payload: Mapping[str, object]) -> FullTextRoute:
    if provider is ProviderName.ARXIV:
        return _route_arxiv(payload)
    if provider in {ProviderName.BIORXIV, ProviderName.MEDRXIV}:
        return _route_rxiv(provider, payload)
    msg = f"provider is not a registered preprint source: {provider}"
    raise ValueError(msg)


def evaluate_pdf_parsers() -> tuple[ParserEvaluation, ...]:
    return (
        ParserEvaluation(
            backend=ParserBackend.DOCLING,
            local_execution=True,
            parses_tables=True,
            parses_formulas=True,
            handles_multi_column=True,
            recommendation="Preferred local/offline parser for scientific PDF to Markdown/JSON extraction.",
        ),
        ParserEvaluation(
            backend=ParserBackend.PDFMUX,
            local_execution=False,
            parses_tables=True,
            parses_formulas=True,
            handles_multi_column=True,
            requires_credentials=True,
            terms_review_required=True,
            recommendation=(
                "Evaluate behind the same parser interface after license, privacy, and deployment terms are approved."
            ),
        ),
    )


def chunk_markdown(
    *,
    work_id: str,
    markdown: str,
    source_locator: str,
    max_chars: int = DEFAULT_CHUNK_CHARS,
) -> tuple[TextChunk, ...]:
    if max_chars < MIN_CHUNK_CHARS:
        msg = f"max_chars must be at least {MIN_CHUNK_CHARS}"
        raise ValueError(msg)
    sections = _split_markdown_sections(markdown)
    chunks: list[TextChunk] = []
    cursor = 0
    for section_path, section_text in sections:
        for piece in _split_text(section_text, max_chars=max_chars):
            start = markdown.find(piece, cursor)
            if start < 0:
                start = cursor
            end = start + len(piece)
            chunk_number = len(chunks) + 1
            chunks.append(
                TextChunk(
                    chunk_id=f"{work_id}:source:{_source_fingerprint(source_locator)}:chunk:{chunk_number}",
                    work_id=work_id,
                    text=piece,
                    source_locator=f"{source_locator}#chunk={chunk_number}",
                    section_path=section_path,
                    start_char=start,
                    end_char=end,
                ),
            )
            cursor = end
    return tuple(chunks)


def create_embedding_records(
    chunks: Sequence[TextChunk],
    vectors: Sequence[Sequence[float]],
    *,
    model_name: str,
) -> tuple[EmbeddingRecord, ...]:
    if len(chunks) != len(vectors):
        msg = "chunks and vectors must have the same length"
        raise ValueError(msg)
    return tuple(
        EmbeddingRecord(chunk_id=chunk.chunk_id, model_name=model_name, vector=tuple(float(item) for item in vector))
        for chunk, vector in zip(chunks, vectors, strict=True)
    )


def build_evidence_set(
    *,
    evidence_set_id: str,
    claim_text: str,
    chunks: Sequence[TextChunk],
    supporting_chunk_ids: Sequence[str],
    provider: ProviderName = ProviderName.UNPAYWALL,
) -> EvidenceSet:
    chunk_by_id = {chunk.chunk_id: chunk for chunk in chunks}
    missing = sorted(set(supporting_chunk_ids) - set(chunk_by_id))
    if missing:
        msg = f"supporting chunks not present: {missing}"
        raise ValueError(msg)
    if len(set(supporting_chunk_ids)) != len(supporting_chunk_ids):
        msg = "supporting_chunk_ids must be unique"
        raise ValueError(msg)
    items = tuple(
        EvidenceItem(
            evidence_id=chunk_by_id[chunk_id].chunk_id,
            source_provider=provider,
            source_locator=chunk_by_id[chunk_id].source_locator,
            quote=chunk_by_id[chunk_id].text,
            context_text=" > ".join(chunk_by_id[chunk_id].section_path) or None,
        )
        for chunk_id in supporting_chunk_ids
    )
    return EvidenceSet(
        evidence_set_id=evidence_set_id,
        claim_text=claim_text,
        items=items,
        supporting_item_ids=tuple(supporting_chunk_ids),
    )


def plan_local_rag_pipeline(routes: Sequence[FullTextRoute]) -> RagPipelinePlan:
    legal_routes = tuple(route for route in routes if route.is_legal and not route.requires_credentials)
    return RagPipelinePlan(
        routes=legal_routes,
        parser_evaluations=evaluate_pdf_parsers(),
    )


def _route_arxiv(payload: Mapping[str, object]) -> FullTextRoute:
    identifier = _text(payload.get("id"))
    if identifier is None:
        msg = "arXiv payload must include id"
        raise ValueError(msg)
    arxiv_id = _normalize_arxiv_id(identifier)
    return FullTextRoute(
        route_id=f"arxiv:{arxiv_id}",
        work_id=f"arxiv:{arxiv_id}",
        source_kind=FullTextSourceKind.ARXIV,
        provider=ProviderName.ARXIV,
        url=f"{ARXIV_PDF_PREFIX}{arxiv_id}.pdf",
        is_legal=True,
        terms_note="Routed through arXiv open preprint access; respect arXiv API and bulk-download terms.",
        source_version=VersionStamp(
            surface=VersionedSurface.PROVIDER,
            name=ProviderName.ARXIV.value,
            version="2026-06-24",
        ),
    )


def _route_rxiv(provider: ProviderName, payload: Mapping[str, object]) -> FullTextRoute:
    collection = payload.get("collection")
    if not isinstance(collection, list) or not collection:
        msg = f"{provider.value} payload must include a non-empty collection"
        raise ValueError(msg)
    collection_items = cast("list[object]", collection)
    first = _mapping(collection_items[0])
    if first is None:
        msg = f"{provider.value} collection item must be an object"
        raise ValueError(msg)
    doi = _text(first.get("doi"))
    if doi is None:
        msg = f"{provider.value} collection item must include doi"
        raise ValueError(msg)
    server = "biorxiv" if provider is ProviderName.BIORXIV else "medrxiv"
    payload_server = _text(first.get("server"))
    if payload_server is not None and payload_server.casefold() != server:
        msg = f"{provider.value} payload server must be {server}"
        raise ValueError(msg)
    normalized_doi = _required_doi(doi)
    source_kind = FullTextSourceKind.BIORXIV if provider is ProviderName.BIORXIV else FullTextSourceKind.MEDRXIV
    return FullTextRoute(
        route_id=f"{provider.value}:{normalized_doi}",
        work_id=f"doi:{normalized_doi}",
        source_kind=source_kind,
        provider=provider,
        url=PREPRINT_PDF_TEMPLATE.format(server=server, doi=normalized_doi),
        doi=normalized_doi,
        license="preprint-server-terms",
        is_legal=True,
        terms_note=f"Routed through {server} open preprint access; respect official API and download terms.",
        source_version=VersionStamp(surface=VersionedSurface.PROVIDER, name=provider.value, version="2026-06-24"),
    )


def _mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    return cast("Mapping[str, object]", value)


def _required_doi(value: str) -> str:
    normalized = normalize_doi(value)
    if normalized is None:
        msg = "DOI is required"
        raise ValueError(msg)
    return normalized


def _text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _split_markdown_sections(markdown: str) -> tuple[tuple[tuple[str, ...], str], ...]:
    current_path: tuple[str, ...] = ("Document",)
    buffer: list[str] = []
    heading_stack: list[str] = []
    sections: list[tuple[tuple[str, ...], str]] = []
    for line in markdown.splitlines():
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading is not None:
            if buffer:
                sections.append((current_path, "\n".join(buffer).strip()))
                buffer = []
            level = len(heading.group(1))
            heading_stack = heading_stack[: level - 1]
            heading_stack.append(heading.group(2).strip())
            current_path = tuple(heading_stack)
            continue
        if line.strip():
            buffer.append(line)
    if buffer:
        sections.append((current_path, "\n".join(buffer).strip()))
    return tuple((path, text) for path, text in sections if text)


def _split_text(text: str, *, max_chars: int) -> tuple[str, ...]:
    if len(text) <= max_chars:
        return (text,)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    buffer = ""
    for sentence in sentences:
        candidate = f"{buffer} {sentence}".strip()
        if len(candidate) <= max_chars:
            buffer = candidate
            continue
        if buffer:
            chunks.append(buffer)
        if len(sentence) > max_chars:
            chunks.extend(_split_long_text(sentence, max_chars=max_chars))
            buffer = ""
            continue
        buffer = sentence
    if buffer:
        chunks.append(buffer)
    return tuple(chunks)


def _split_long_text(text: str, *, max_chars: int) -> tuple[str, ...]:
    return tuple(text[start : start + max_chars] for start in range(0, len(text), max_chars))


def _legal_pdf_url(value: str | None) -> str | None:
    if value is None:
        return None
    parsed = urlparse(value)
    if parsed.scheme.lower() != LEGAL_FULL_TEXT_SCHEME or not parsed.netloc or not parsed.path.lower().endswith(".pdf"):
        return None
    return value


def _normalize_arxiv_id(identifier: str) -> str:
    parsed = urlparse(identifier)
    if parsed.scheme:
        if parsed.hostname != ARXIV_HOST or not parsed.path.startswith("/abs/"):
            msg = "arXiv payload id must be a bare arXiv ID or arxiv.org abs URL"
            raise ValueError(msg)
        identifier = parsed.path.removeprefix("/abs/")
    if not ARXIV_ID_RE.fullmatch(identifier):
        msg = "arXiv payload id has an invalid format"
        raise ValueError(msg)
    return identifier


def _source_fingerprint(source_locator: str) -> str:
    return sha256(source_locator.encode("utf-8")).hexdigest()[:SOURCE_FINGERPRINT_LENGTH]
