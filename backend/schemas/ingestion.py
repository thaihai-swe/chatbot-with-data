from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class UrlIngestionRequest(BaseModel):
    url: HttpUrl
    collection_ids: list[str] = Field(default_factory=list)


class IngestionAttemptResponse(BaseModel):
    id: str
    document_id: str | None = None
    source_type: str
    status: str
    submitted_filename: str | None = None
    source_uri: str | None = None
    canonical_source_uri: str | None = None
    mime_type: str | None = None
    artifact_path: str | None = None
    snapshot_path: str | None = None
    title: str | None = None
    metadata_json: str
    file_hash: str | None = None
    normalized_text_hash: str | None = None
    duplicate_status: str | None = None
    duplicate_match_document_id: str | None = None
    duplicate_evidence_json: str | None = None
    error_message: str | None = None
    collection_ids: list[str] = Field(default_factory=list)
    created_at: str
    updated_at: str
    completed_at: str | None = None


class DuplicateCheckResult(BaseModel):
    classification: str
    matched_document_id: str | None = None
    detection_method: str
    evidence: dict[str, Any] = Field(default_factory=dict)
