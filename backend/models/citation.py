from dataclasses import dataclass


@dataclass
class Citation:
    citation_id: str
    cited_chunk_id: str
    document_id: str
    document_title: str | None
    page_or_section: str | None
    source_url: str | None
    content_snippet: str
    retrieval_score: float | None
    retrieval_mode: str
    inline_text_reference: str | None = None
    embedding_or_rerank_score: float | None = None
    citation_order: int = 0

    def to_dict(self):
        return {
            "citation_id": self.citation_id,
            "chunk_id": self.cited_chunk_id,
            "document_id": self.document_id,
            "document_title": self.document_title,
            "page_or_section": self.page_or_section,
            "source_url": self.source_url,
            "content_snippet": self.content_snippet,
            "retrieval_score": self.retrieval_score,
            "retrieval_mode": self.retrieval_mode,
            "inline_text_reference": self.inline_text_reference,
            "embedding_or_rerank_score": self.embedding_or_rerank_score,
            "citation_order": self.citation_order,
        }
