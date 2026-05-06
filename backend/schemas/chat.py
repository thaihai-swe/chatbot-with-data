from __future__ import annotations

from typing import Optional, List, Any
from pydantic import BaseModel, Field


class ChatSessionCreate(BaseModel):
    collection_id: Optional[str] = Field(None, description="Collection ID to scope the chat. None for all collections.")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict)


class ChatSessionResponse(BaseModel):
    id: str
    collection_id: Optional[str]
    metadata_json: str
    created_at: str
    updated_at: str


class ChatTurnCreate(BaseModel):
    query_text: str = Field(..., min_length=1)


class CitationResponse(BaseModel):
    id: str
    turn_id: str
    chunk_id: str
    document_id: str
    quote_text: Optional[str]
    metadata_json: str
    created_at: str


class ChatTurnResponse(BaseModel):
    id: str
    session_id: str
    query_text: str
    answer_text: Optional[str]
    retrieved_chunks_json: str
    context_used_json: str
    status: str
    error_message: Optional[str]
    created_at: str
    updated_at: str
    citations: List[CitationResponse] = []
