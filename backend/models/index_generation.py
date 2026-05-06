from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from models.enums import IndexGenerationStatus


@dataclass
class IndexGeneration:
    """
    Represents a single index generation for a document.
    Tracks when embeddings and vectors were generated, what strategy was used,
    and whether this generation is currently active for queries.
    """

    id: str
    document_id: str
    generation_number: int
    status: IndexGenerationStatus
    strategy: str
    chunk_count: int
    is_active: bool
    settings_hash: Optional[str] = None
    embedding_model: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

    def __post_init__(self):
        """Validate fields after initialization."""
        if not self.id:
            raise ValueError("id is required")
        if not self.document_id:
            raise ValueError("document_id is required")
        if self.generation_number < 0:
            raise ValueError("generation_number must be >= 0")
        if not self.strategy:
            raise ValueError("strategy is required")
        if self.chunk_count < 0:
            raise ValueError("chunk_count must be >= 0")
        if isinstance(self.status, str):
            self.status = IndexGenerationStatus(self.status)
