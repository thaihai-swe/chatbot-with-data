from __future__ import annotations

from repositories.chunk_repository import ChunkRepository
from chunking.dispatcher import ChunkingDispatcher


class ChunkingService:
    """Orchestrates document chunking and persistence."""

    def __init__(self):
        self.chunk_repo = ChunkRepository()
        self.dispatcher = ChunkingDispatcher()

    def chunk_document(
        self,
        document_id: str,
        collection_id: str,
        text: str,
        *,
        strategy: str = "fixed_size",
        source_type: str = "text",
        title: str | None = None,
        page_number: int | None = None,
        source_url: str | None = None,
        chunk_size: int = 512,
        overlap: int = 0,
        metadata: dict | None = None,
    ) -> list[dict]:
        """
        Chunk a document and persist chunks to database.

        Args:
            document_id: Unique document identifier
            collection_id: Collection identifier
            text: Document text content
            strategy: Chunking strategy to use
            source_type: Document source type (pdf, txt, md, url)
            title: Document title
            page_number: Starting page number
            source_url: Source URL
            chunk_size: Target chunk size in tokens
            overlap: Overlap in tokens
            metadata: Additional metadata

        Returns:
            List of created chunk dictionaries
        """
        metadata = metadata or {}

        # Use dispatcher to chunk
        chunk_data_list = self.dispatcher.chunk(
            text,
            strategy=strategy,
            source_type=source_type,
            title=title,
            page_number=page_number,
            source_url=source_url,
            chunk_size=chunk_size,
            overlap=overlap,
            metadata=metadata,
        )

        # Persist chunks
        persisted_chunks = []
        for chunk_data in chunk_data_list:
            chunk = self.chunk_repo.create_chunk(
                document_id=document_id,
                collection_id=collection_id,
                chunk_order=chunk_data.chunk_order,
                strategy=strategy,
                source_type=source_type,
                title=chunk_data.title,
                section_title=chunk_data.section_title,
                page_number=chunk_data.page_number,
                source_url=chunk_data.source_url,
                text=chunk_data.text,
                parent_chunk_id=None,  # Set by parent-child strategy
                fallback_applied=chunk_data.fallback_applied,
                semantic_score=chunk_data.semantic_score,
                metadata=chunk_data.metadata,
            )
            persisted_chunks.append(chunk)

        return persisted_chunks

    def delete_document_chunks(self, document_id: str) -> int:
        """Delete all chunks for a document."""
        return self.chunk_repo.delete_chunks_by_document(document_id)

    def get_document_chunks(
        self,
        document_id: str,
        strategy: str | None = None,
    ) -> list[dict]:
        """Get all chunks for a document, optionally filtered by strategy."""
        return self.chunk_repo.list_chunks_by_document(
            document_id, strategy=strategy
        )

    def count_document_chunks(self, document_id: str) -> int:
        """Count chunks for a document."""
        return self.chunk_repo.count_chunks_by_document(document_id)


def get_chunking_service() -> ChunkingService:
    """Factory function for ChunkingService."""
    return ChunkingService()
