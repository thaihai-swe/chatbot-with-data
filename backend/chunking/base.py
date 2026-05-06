from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ChunkData:
    """Represents a single chunk with metadata."""

    chunk_order: int
    text: str
    title: str | None = None
    section_title: str | None = None
    page_number: int | None = None
    source_url: str | None = None
    fallback_applied: bool = False
    semantic_score: float | None = None
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseChunker(ABC):
    """Abstract base class for chunking strategies."""

    def __init__(
        self,
        chunk_size: int = 512,
        overlap: int = 0,
    ):
        """
        Initialize chunker with common parameters.

        Args:
            chunk_size: Target chunk size in tokens (approximate)
            overlap: Number of tokens to overlap between chunks (0-50% of chunk_size)
        """
        self.chunk_size = max(1, chunk_size)
        self.overlap = max(0, min(overlap, int(chunk_size * 0.5)))

    @abstractmethod
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
        Chunk the text using the strategy-specific approach.

        Args:
            text: The text to chunk
            source_type: Type of source (pdf, txt, md, url)
            title: Document title
            page_number: Page number (for PDF)
            source_url: Source URL (for web content)
            metadata: Additional metadata to attach

        Returns:
            List of ChunkData objects
        """
        pass

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Rough token count estimate (words * 1.3)."""
        return int(len(text.split()) * 1.3)
