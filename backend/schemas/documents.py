from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from models.enums import DuplicateAction


class CollectionMembership(BaseModel):
    id: str
    name: str


class DocumentSummary(BaseModel):
    id: str
    title: str
    source_type: str
    source_uri: str | None = None
    filename: str | None = None
    latest_status: str | None = None
    latest_duplicate_status: str | None = None
    created_at: str
    updated_at: str
    metadata: dict[str, Any]
    collections: list[CollectionMembership]


class DocumentResponse(DocumentSummary):
    canonical_source_uri: str | None = None
    mime_type: str | None = None
    file_hash: str | None = None
    normalized_text_hash: str | None = None
    extracted_text: str
    latest_attempt: dict[str, Any] | None = None


class DocumentMoveRequest(BaseModel):
    collection_ids: list[str] = Field(default_factory=list)


class DuplicateDecisionRequest(BaseModel):
    action: DuplicateAction


class ReingestRequest(BaseModel):
    collection_ids: list[str] = Field(default_factory=list)
