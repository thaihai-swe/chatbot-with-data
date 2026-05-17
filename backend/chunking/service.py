from __future__ import annotations

from config import get_config
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
        chunk_size: int | None = None,
        overlap: int | None = None,
        metadata: dict | None = None,
    ) -> list[dict]:
        """
        Chunk a document and persist chunks to database.
        """
        config = get_config()
        chunk_size = chunk_size or config.ingestion.chunk_size
        overlap = overlap if overlap is not None else config.ingestion.chunk_overlap

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
