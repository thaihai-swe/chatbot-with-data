"""Collection model for RAG accuracy fixes."""
from __future__ import annotations

from typing import Optional


class Collection:
    """Represents a collection of documents."""

    def __init__(
        self,
        id: str,
        name: str,
        description: Optional[str] = None,
        is_default: bool = False,
        routing_enabled: bool = False,
        min_similarity_threshold: Optional[float] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.is_default = is_default
        self.routing_enabled = routing_enabled
        self.min_similarity_threshold = min_similarity_threshold
        self.created_at = created_at
        self.updated_at = updated_at