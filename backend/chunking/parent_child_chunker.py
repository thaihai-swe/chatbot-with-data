from __future__ import annotations

import re

from chunking.base import BaseChunker, ChunkData
from repositories.chunk_repository import ChunkRepository


class ParentChildChunker(BaseChunker):
    """Chunking strategy that creates parent-child chunk relationships.

    Parents are aligned to heading boundaries when headings are detected.
    Falls back to fixed children_per_parent grouping for unstructured text.
    """

    def __init__(
        self,
        chunk_size: int = 512,
        overlap: int = 0,
        children_per_parent: int = 4,
    ):
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
        from chunking.fixed_size_chunker import FixedSizeChunker

        if not text or not text.strip():
            return []

        metadata = metadata or {}

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

        # Detect heading boundaries for grouping
        section_boundaries = self._detect_section_boundaries(text)

        if section_boundaries:
            parent_groups = self._group_by_boundaries(child_chunks, section_boundaries)
        else:
            parent_groups = self._group_fixed_count(child_chunks)

        all_chunks = list(child_chunks)
        parent_order = len(child_chunks) + 1

        for group in parent_groups:
            parent_text = " ".join([c.text for c in group])
            parent_chunk = ChunkData(
                chunk_order=parent_order,
                text=parent_text,
                title=title,
                section_title="Expanded Context",
                page_number=page_number,
                source_url=source_url,
                metadata={**metadata, "parent_chunk": True, "children_count": len(group)}
            )
            all_chunks.append(parent_chunk)
            parent_order += 1

        return all_chunks

    def _detect_section_boundaries(self, text: str) -> list[int]:
        """Find character positions of heading boundaries in text."""
        boundaries = []
        for match in re.finditer(r'^#{1,6}\s+.+$', text, re.MULTILINE):
            boundaries.append(match.start())
        return boundaries

    def _group_by_boundaries(
        self,
        child_chunks: list[ChunkData],
        boundaries: list[int],
    ) -> list[list[ChunkData]]:
        """Group child chunks by which section boundary they fall under."""
        if not child_chunks:
            return []

        groups: list[list[ChunkData]] = []
        boundary_idx = 0
        current_group: list[ChunkData] = []

        # Estimate token offset to find section transitions
        for chunk in child_chunks:
            current_group.append(chunk)
            if boundary_idx < len(boundaries):
                chunk_start_token = chunk.chunk_order * self.chunk_size
                boundary_token = int(boundaries[boundary_idx] * 1.3)
                if chunk_start_token > boundary_token:
                    groups.append(current_group)
                    current_group = []
                    boundary_idx += 1

        if current_group:
            groups.append(current_group)

        return groups if groups else [child_chunks]

    def _group_fixed_count(self, child_chunks: list[ChunkData]) -> list[list[ChunkData]]:
        groups = []
        for i in range(0, len(child_chunks), self.children_per_parent):
            groups.append(child_chunks[i:i + self.children_per_parent])
        return groups

    @classmethod
    def create_parent_child_relationships(
        cls,
        chunks: list[dict],
        children_per_parent: int = 4,
        repo: ChunkRepository | None = None,
    ) -> None:
        if not repo:
            repo = ChunkRepository()

        child_chunks = [c for c in chunks if not c.get("metadata", {}).get("parent_chunk")]
        parent_chunks = [c for c in chunks if c.get("metadata", {}).get("parent_chunk")]

        for parent_idx, parent_chunk in enumerate(parent_chunks):
            start_child_idx = parent_idx * children_per_parent
            end_child_idx = min(start_child_idx + children_per_parent, len(child_chunks))
            child_group = child_chunks[start_child_idx:end_child_idx]

            for child_chunk in child_group:
                repo.update_chunk(
                    child_chunk["id"],
                    metadata={**child_chunk.get("metadata", {}), "parent_chunk_id": parent_chunk["id"]}
                )
