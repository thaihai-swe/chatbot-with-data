from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from database import get_connection
from schemas.notes import NoteResponse, NoteUpsertRequest


router = APIRouter(tags=["notes"])


def _chunk_exists(chunk_id: str) -> bool:
    with get_connection() as connection:
        return bool(connection.execute("SELECT 1 FROM chunks WHERE id = ?", (chunk_id,)).fetchone())


@router.get("/chunks/{chunk_id}/notes", response_model=NoteResponse | None)
def get_chunk_note(chunk_id: str) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT chunk_id, note_text, created_at, updated_at FROM chunk_notes WHERE chunk_id = ?",
            (chunk_id,),
        ).fetchone()
    if not row:
        return None
    return dict(row)


@router.put("/chunks/{chunk_id}/notes", response_model=NoteResponse)
def upsert_chunk_note(chunk_id: str, payload: NoteUpsertRequest) -> dict:
    if not _chunk_exists(chunk_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chunk not found")
    now = datetime.now(UTC).isoformat()
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT 1 FROM chunk_notes WHERE chunk_id = ?", (chunk_id,)
        ).fetchone()
        if existing:
            connection.execute(
                "UPDATE chunk_notes SET note_text = ?, updated_at = ? WHERE chunk_id = ?",
                (payload.note_text, now, chunk_id),
            )
        else:
            connection.execute(
                "INSERT INTO chunk_notes (chunk_id, note_text, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (chunk_id, payload.note_text, now, now),
            )
    return NoteResponse(chunk_id=chunk_id, note_text=payload.note_text, created_at=now, updated_at=now).model_dump()
