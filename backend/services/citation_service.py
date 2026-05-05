from backend.models.citation import Citation
from backend.utils import generate_id


class CitationFormattingService:
    def _page_or_section(self, chunk):
        return chunk.get("page_or_section") or (f"page {chunk['page_number']}" if chunk.get("page_number") else chunk.get("section_name"))

    def format_citations(self, retrieved_chunks, citation_indices=None, retrieval_mode="semantic"):
        citations = []
        if citation_indices is None:
            citation_indices = list(range(len(retrieved_chunks[:3])))
        for order, index in enumerate(citation_indices, start=1):
            if index < 0 or index >= len(retrieved_chunks):
                continue
            chunk = retrieved_chunks[index]
            citation = Citation(
                citation_id=generate_id("cit"),
                cited_chunk_id=chunk["chunk_id"],
                document_id=chunk["document_id"],
                document_title=chunk.get("document_title"),
                page_or_section=self._page_or_section(chunk),
                source_url=chunk.get("source_url"),
                content_snippet=(chunk.get("full_text") or chunk.get("content_snippet") or "").strip()[:320],
                retrieval_score=chunk.get("retrieval_score"),
                retrieval_mode=chunk.get("retrieval_mode") or retrieval_mode,
                inline_text_reference=f"[{order}]",
                citation_order=order,
            )
            citations.append(citation.to_dict())
        return citations
