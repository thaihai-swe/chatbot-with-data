from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime
from typing import Any

from database import get_connection


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


class ChunkRepository:
    """Data access layer for chunk records."""

    def create_chunk(
        self,
        *,
        document_id: str,
        collection_id: str,
        chunk_order: int,
        strategy: str,
        source_type: str,
        title: str | None,
        section_title: str | None,
        page_number: int | None,
        source_url: str | None,
        text: str,
        parent_chunk_id: str | None = None,
        fallback_applied: bool = False,
        semantic_score: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        chunk_id = str(uuid.uuid4())
        now = _utc_now()
        metadata = metadata or {}

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO chunks(
                    id, document_id, collection_id, chunk_order, strategy, source_type,
                    title, section_title, page_number, source_url, text, text_length,
                    parent_chunk_id, fallback_applied, semantic_score, metadata_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk_id,
                    document_id,
                    collection_id,
                    chunk_order,
                    strategy,
                    source_type,
                    title,
                    section_title,
                    page_number,
                    source_url,
                    text,
                    len(text),
                    parent_chunk_id,
                    int(fallback_applied),
                    semantic_score,
                    json.dumps(metadata),
                    now,
                ),
            )
        return self.get_chunk(chunk_id)

    def get_chunk(self, chunk_id: str) -> dict[str, Any] | None:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM chunks WHERE id = ?",
                (chunk_id,),
            ).fetchone()
        if not row:
            return None
        record = dict(row)
        record["metadata"] = json.loads(record.pop("metadata_json"))
        record["fallback_applied"] = bool(record["fallback_applied"])
        return record

    def list_chunks_by_document(
        self,
        document_id: str,
        strategy: str | None = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        with get_connection() as connection:
            query = "SELECT * FROM chunks WHERE document_id = ?"
            params = [document_id]

            if strategy:
                query += " AND strategy = ?"
                params.append(strategy)

            query += " ORDER BY chunk_order ASC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            rows = connection.execute(query, params).fetchall()

        records = []
        for row in rows:
            record = dict(row)
            record["metadata"] = json.loads(record.pop("metadata_json"))
            record["fallback_applied"] = bool(record["fallback_applied"])
            records.append(record)
        return records

    def list_chunks_by_collection(
        self,
        collection_id: str,
        limit: int = 1000,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM chunks
                WHERE collection_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (collection_id, limit, offset),
            ).fetchall()

        records = []
        for row in rows:
            record = dict(row)
            record["metadata"] = json.loads(record.pop("metadata_json"))
            record["fallback_applied"] = bool(record["fallback_applied"])
            records.append(record)
        return records

    def get_chunks_by_parent_id(self, parent_chunk_id: str) -> list[dict[str, Any]]:
        """Get all child chunks for a given parent chunk."""
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM chunks
                WHERE parent_chunk_id = ?
                ORDER BY chunk_order ASC
                """,
                (parent_chunk_id,),
            ).fetchall()

        records = []
        for row in rows:
            record = dict(row)
            record["metadata"] = json.loads(record.pop("metadata_json"))
            record["fallback_applied"] = bool(record["fallback_applied"])
            records.append(record)
        return records

    def update_chunk(
        self,
        chunk_id: str,
        *,
        strategy: str | None = None,
        fallback_applied: bool | None = None,
        semantic_score: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        current = self.get_chunk(chunk_id)
        if not current:
            return None

        update_values = {
            "strategy": strategy if strategy is not None else current["strategy"],
            "fallback_applied": (
                int(fallback_applied)
                if fallback_applied is not None
                else current["fallback_applied"]
            ),
            "semantic_score": (
                semantic_score if semantic_score is not None else current["semantic_score"]
            ),
            "metadata_json": json.dumps(
                metadata if metadata is not None else current["metadata"]
            ),
        }

        with get_connection() as connection:
            set_clause = ", ".join(f"{k} = ?" for k in update_values.keys())
            query = f"UPDATE chunks SET {set_clause} WHERE id = ?"
            connection.execute(query, list(update_values.values()) + [chunk_id])

        return self.get_chunk(chunk_id)

    def delete_chunk(self, chunk_id: str) -> bool:
        """Delete a chunk and its children (cascading delete)."""
        with get_connection() as connection:
            # This will cascade delete due to foreign key constraints
            row = connection.execute(
                "DELETE FROM chunks WHERE id = ?",
                (chunk_id,),
            )
        return row.rowcount > 0

    def delete_chunks_by_document(self, document_id: str) -> int:
        """Delete all chunks for a document."""
        with get_connection() as connection:
            row = connection.execute(
                "DELETE FROM chunks WHERE document_id = ?",
                (document_id,),
            )
        return row.rowcount

    def count_chunks_by_document(self, document_id: str) -> int:
        """Get total chunk count for a document."""
        with get_connection() as connection:
            row = connection.execute(
                "SELECT COUNT(*) as count FROM chunks WHERE document_id = ?",
                (document_id,),
            ).fetchone()
        return row["count"] if row else 0
