from __future__ import annotations

from pydantic import BaseModel, Field


NOTE_TEXT_MAX_LENGTH = 2000


class NoteResponse(BaseModel):
    chunk_id: str
    note_text: str
    created_at: str | None = None
    updated_at: str | None = None


class NoteUpsertRequest(BaseModel):
    note_text: str = Field(..., max_length=NOTE_TEXT_MAX_LENGTH)
