from dataclasses import dataclass
from typing import Optional


@dataclass
class Embedding:
    """Represents a cached embedding vector."""

    id: str
    chunk_id: str
    embedding_model: str
    embedding_model_version: Optional[str]
    embedding_vector: list[float]  # Vector stored as JSON or BLOB
    input_text_hash: str
    created_at: str

    def __post_init__(self):
        """Validate embedding properties."""
        if not self.id:
            raise ValueError("Embedding ID cannot be empty")
        if not self.chunk_id:
            raise ValueError("Chunk ID cannot be empty")
        if not self.embedding_model:
            raise ValueError("Embedding model cannot be empty")
        if not self.embedding_vector or not isinstance(self.embedding_vector, list):
            raise ValueError("Embedding vector must be a non-empty list")
        if not self.input_text_hash:
            raise ValueError("Input text hash cannot be empty")
