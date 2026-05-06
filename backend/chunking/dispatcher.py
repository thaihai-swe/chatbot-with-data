from __future__ import annotations

from typing import TYPE_CHECKING

from chunking.fixed_size_chunker import FixedSizeChunker
from chunking.heading_aware_chunker import HeadingAwareChunker
from chunking.page_aware_chunker import PageAwareChunker
from chunking.parent_child_chunker import ParentChildChunker
from chunking.semantic_chunker import SemanticChunker

if TYPE_CHECKING:
    from chunking.base import ChunkData


class ChunkingDispatcher:
    """Routes chunking requests to appropriate strategy."""

    STRATEGIES = {
        "fixed_size": FixedSizeChunker,
        "heading_aware": HeadingAwareChunker,
        "page_aware": PageAwareChunker,
        "parent_child": ParentChildChunker,
        "semantic": SemanticChunker,
    }

    DEFAULT_STRATEGY_BY_SOURCE = {
        "pdf": "page_aware",
        "md": "heading_aware",
        "txt": "fixed_size",
        "url": "heading_aware",
    }

    @staticmethod
    def get_default_strategy(source_type: str) -> str:
        """Get recommended strategy for source type."""
        return ChunkingDispatcher.DEFAULT_STRATEGY_BY_SOURCE.get(
            source_type.lower(), "fixed_size"
        )

    @staticmethod
    def chunk(
        text: str,
        strategy: str = "fixed_size",
        *,
        source_type: str = "text",
        title: str | None = None,
        page_number: int | None = None,
        source_url: str | None = None,
        chunk_size: int = 512,
        overlap: int = 0,
        metadata: dict | None = None,
    ) -> list[ChunkData]:
        """
        Chunk text using specified strategy.

        Args:
            text: Text to chunk
            strategy: Strategy name (fixed_size, heading_aware, page_aware)
            source_type: Type of source (pdf, txt, md, url)
            title: Document title
            page_number: Starting page number (for PDF)
            source_url: Source URL
            chunk_size: Target chunk size in tokens
            overlap: Overlap in tokens
            metadata: Additional metadata

        Returns:
            List of ChunkData objects
        """
        if strategy not in ChunkingDispatcher.STRATEGIES:
            raise ValueError(
                f"Unknown strategy: {strategy}. "
                f"Available: {list(ChunkingDispatcher.STRATEGIES.keys())}"
            )

        chunker_class = ChunkingDispatcher.STRATEGIES[strategy]
        chunker = chunker_class(chunk_size=chunk_size, overlap=overlap)

        return chunker.chunk(
            text,
            source_type=source_type,
            title=title,
            page_number=page_number,
            source_url=source_url,
            metadata=metadata,
        )

    @staticmethod
    def get_available_strategies() -> list[str]:
        """Get list of available strategies."""
        return list(ChunkingDispatcher.STRATEGIES.keys())
