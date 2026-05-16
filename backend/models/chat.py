from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class ChatSession:
    """
    Represents a chat session with a user.
    """
    id: str
    collection_ids: List[str] = field(default_factory=list)  # Empty means 'all collections'
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata_json: str = "{}"

    def __post_init__(self):
        if not self.id:
            raise ValueError("id is required")


@dataclass
class ChatTurn:
    """
    Represents a single turn (query/answer pair) in a chat session.
    """
    id: str
    session_id: str
    query_text: str
    answer_text: Optional[str] = None
    retrieved_chunks_json: str = "[]"  # List of chunk IDs or full metadata
    context_used_json: str = "{}"  # Prompt and retrieval results used
    status: str = "pending"  # pending, generating, completed, error, cancelled
    safety_status: Optional[str] = None
    safety_risk_score: Optional[float] = None
    safety_reason: Optional[str] = None
    groundedness_score: Optional[float] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        if not self.id:
            raise ValueError("id is required")
        if not self.session_id:
            raise ValueError("session_id is required")
        if not self.query_text:
            raise ValueError("query_text is required")


@dataclass
class Citation:
    """
    Represents a citation linking a chat turn to a source chunk.
    """
    id: str
    turn_id: str
    chunk_id: str
    document_id: str
    quote_text: Optional[str] = None  # Optional specific quote from the chunk
    metadata_json: str = "{}"  # Additional metadata (page, section, etc.)
    created_at: Optional[str] = None

    def __post_init__(self):
        if not self.id:
            raise ValueError("id is required")
        if not self.turn_id:
            raise ValueError("turn_id is required")
        if not self.chunk_id:
            raise ValueError("chunk_id is required")
        if not self.document_id:
            raise ValueError("document_id is required")
