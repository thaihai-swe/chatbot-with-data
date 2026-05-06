from __future__ import annotations

from chunking.base import BaseChunker, ChunkData
from repositories.chunk_repository import ChunkRepository


class ParentChildChunker(BaseChunker):
    """Chunking strategy that creates parent-child chunk relationships."""

    def __init__(
        self,
        chunk_size: int = 512,
        overlap: int = 0,
        children_per_parent: int = 4,
    ):
        """
        Initialize parent-child chunker.

        Args:
            chunk_size: Target size for child chunks
            overlap: Overlap between child chunks
            children_per_parent: How many child chunks per parent
        """
        super().__init__(chunk_size=chunk_size, overlap=overlap)
        self.children_per_parent = max(1, children_per_parent)

    def chunk(
        self,
        text: str,
        *,
        source_type: str = "text",
        title: str | None = None,
        page_number: int | None = None,
        source_url: str | None = None,
        metadata: dict | None = None,
    ) -> list[ChunkData]:
        """
        Create parent-child chunk relationships.

        The approach:
        1. First create child chunks using fixed-size strategy
        2. Group child chunks into parent units
        3. Return both parent and child chunks with relationship links
        """
        from chunking.fixed_size_chunker import FixedSizeChunker

        if not text or not text.strip():
            return []

        metadata = metadata or {}

        # Create child chunks first
        fixed_chunker = FixedSizeChunker(
            chunk_size=self.chunk_size,
            overlap=self.overlap
        )

        child_chunks = fixed_chunker.chunk(
            text,
            source_type=source_type,
            title=title,
            page_number=page_number,
            source_url=source_url,
            metadata=metadata,
        )

        if not child_chunks:
            return []

        # Create parent chunks from groups of children
        # Note: parent_chunk_id will be set by the service layer after persistence
        all_chunks = []
        parent_order = 1
        child_order = len(child_chunks) + 1  # Parent chunks come after children

        for i in range(0, len(child_chunks), self.children_per_parent):
            child_group = child_chunks[i : i + self.children_per_parent]

            # Create parent chunk text from children
            parent_text = " ".join([c.text for c in child_group])

            parent_chunk = ChunkData(
                chunk_order=child_order,
                text=parent_text,
                title=title,
                section_title="Expanded Context",
                page_number=page_number,
                source_url=source_url,
                metadata={**metadata, "parent_chunk": True, "children_count": len(child_group)}
            )

            all_chunks.append(parent_chunk)
            child_order += 1

        # Return children first, then parents
        return child_chunks + all_chunks

    @classmethod
    def create_parent_child_relationships(
        cls,
        chunks: list[dict],
        children_per_parent: int = 4,
        repo: ChunkRepository | None = None,
    ) -> None:
        """
        Create parent-child relationships between existing chunks.

        This is used after chunks are persisted to establish the bidirectional links.
        """
        if not repo:
            repo = ChunkRepository()

        # Separate parent and child chunks
        child_chunks = [c for c in chunks if not c.get("metadata", {}).get("parent_chunk")]
        parent_chunks = [c for c in chunks if c.get("metadata", {}).get("parent_chunk")]

        # Link parents to children
        for parent_idx, parent_chunk in enumerate(parent_chunks):
            # Get the range of children for this parent
            start_child_idx = parent_idx * children_per_parent
            end_child_idx = min(start_child_idx + children_per_parent, len(child_chunks))

            child_group = child_chunks[start_child_idx:end_child_idx]

            # Update each child with parent_id
            for child_chunk in child_group:
                repo.update_chunk(
                    child_chunk["id"],
                    metadata={**child_chunk.get("metadata", {}), "parent_chunk_id": parent_chunk["id"]}
                )
