from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class IndexEntry:
    """
    Represents a single entry in the vector index.
    Links chunks to their embeddings and tracks which generation they belong to.
    Supports marking entries as inactive when re-indexing.
    """

    id: str
    chunk_id: str
    embedding_id: str
    document_id: str
    collection_id: str
    generation_id: str
    chunk_order: int
    is_active: bool = True
    vector_db_id: Optional[str] = None
    parent_chunk_id: Optional[str] = None
    created_at: Optional[str] = None

    def __post_init__(self):
        """Validate fields after initialization."""
        if not self.id:
            raise ValueError("id is required")
        if not self.chunk_id:
            raise ValueError("chunk_id is required")
        if not self.embedding_id:
            raise ValueError("embedding_id is required")
        if not self.document_id:
            raise ValueError("document_id is required")
        if not self.collection_id:
            raise ValueError("collection_id is required")
        if not self.generation_id:
            raise ValueError("generation_id is required")
        if self.chunk_order < 0:
            raise ValueError("chunk_order must be >= 0")
