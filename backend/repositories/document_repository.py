from __future__ import annotations

import json
import uuid
from typing import Any

from database import get_connection
from repositories.base import BaseRepository, _utc_now


class DocumentRepository(BaseRepository):
    def create_document(
        self,
        *,
        title: str,
        source_type: str,
        source_uri: str | None,
        canonical_source_uri: str | None,
        filename: str | None,
        mime_type: str | None,
        file_hash: str | None,
        normalized_text_hash: str | None,
        extracted_text: str,
        metadata: dict[str, Any],
        collection_ids: list[str],
        version_of_document_id: str | None = None,
        document_id: str | None = None,
    ) -> dict[str, Any]:
        document_id = document_id or str(uuid.uuid4())
        now = _utc_now()
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO documents(
                    id, title, source_type, source_uri, canonical_source_uri, filename, mime_type,
                    file_hash, normalized_text_hash, extracted_text, metadata_json, version_of_document_id,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id, title, source_type, source_uri, canonical_source_uri,
                    filename, mime_type, file_hash, normalized_text_hash, extracted_text,
                    json.dumps(metadata), version_of_document_id, now, now,
                ),
            )
            for collection_id in collection_ids:
                connection.execute(
                    "INSERT OR IGNORE INTO document_collections(document_id, collection_id, created_at) VALUES (?, ?, ?)",
                    (document_id, collection_id, now),
                )
            self._create_lifecycle_event(
                connection,
                document_id=document_id,
                ingestion_attempt_id=None,
                event_type="document_created",
                from_status=None,
                to_status=None,
                details={"collection_ids": collection_ids},
            )
        return self.get_document(document_id)

    def update_document(
        self,
        document_id: str,
        *,
        title: str | None = None,
        source_uri: str | None = None,
        canonical_source_uri: str | None = None,
        filename: str | None = None,
        mime_type: str | None = None,
        file_hash: str | None = None,
        normalized_text_hash: str | None = None,
        extracted_text: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        current = self.get_document(document_id)
        if not current:
            return None
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE documents
                SET title = ?, source_uri = ?, canonical_source_uri = ?, filename = ?,
                    mime_type = ?, file_hash = ?, normalized_text_hash = ?, extracted_text = ?,
                    metadata_json = ?, updated_at = ?
                WHERE id = ? AND deleted_at IS NULL
                """,
                (
                    title if title is not None else current["title"],
                    source_uri if source_uri is not None else current["source_uri"],
                    canonical_source_uri if canonical_source_uri is not None else current["canonical_source_uri"],
                    filename if filename is not None else current["filename"],
                    mime_type if mime_type is not None else current["mime_type"],
                    file_hash if file_hash is not None else current["file_hash"],
                    normalized_text_hash if normalized_text_hash is not None else current["normalized_text_hash"],
                    extracted_text if extracted_text is not None else current["extracted_text"],
                    json.dumps(metadata if metadata is not None else current["metadata"]),
                    _utc_now(),
                    document_id,
                ),
            )
        return self.get_document(document_id)

    def get_document(self, document_id: str) -> dict[str, Any] | None:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE id = ? AND deleted_at IS NULL",
                (document_id,),
            ).fetchone()
            if not row:
                return None
            collection_rows = connection.execute(
                """
                SELECT c.id, c.name FROM collections c
                JOIN document_collections dc ON dc.collection_id = c.id
                WHERE dc.document_id = ? AND c.deleted_at IS NULL
                ORDER BY c.name
                """,
                (document_id,),
            ).fetchall()
            latest_attempt = connection.execute(
                "SELECT * FROM ingestion_attempts WHERE document_id = ? ORDER BY created_at DESC LIMIT 1",
                (document_id,),
            ).fetchone()
            chunk_rows = connection.execute(
                """
                SELECT id, title, page_number, chunk_order, text as content
                FROM chunks
                WHERE document_id = ?
                ORDER BY chunk_order ASC
                """,
                (document_id,),
            ).fetchall()
        record = dict(row)
        record["metadata"] = json.loads(record.pop("metadata_json"))
        record["collections"] = [dict(item) for item in collection_rows]
        record["latest_attempt"] = dict(latest_attempt) if latest_attempt else None
        record["chunks"] = [dict(item) for item in chunk_rows]
        record["chunk_count"] = len(record["chunks"])
        return record

    def get_document_batch(self, ids: list[str]) -> dict[str, dict[str, Any]]:
        """Fetch multiple documents by ID.

        Args:
            ids: List of document IDs

        Returns:
            Dict mapping document ID to {title, metadata}
        """
        if not ids:
            return {}
        placeholders = ",".join("?" for _ in ids)
        with get_connection() as connection:
            rows = connection.execute(
                f"SELECT id, title, metadata_json FROM documents WHERE id IN ({placeholders}) AND deleted_at IS NULL",
                ids,
            ).fetchall()
        result = {}
        for row in rows:
            record = dict(row)
            record["metadata"] = json.loads(record.pop("metadata_json"))
            result[record["id"]] = record
        return result

    def list_documents(
        self,
        *,
        collection_id: str | None = None,
        search_query: str | None = None,
    ) -> list[dict[str, Any]]:
        filters: list[str] = ["d.deleted_at IS NULL"]
        params: list[Any] = []
        join_clause = ""
        if collection_id:
            join_clause = "JOIN document_collections filter_dc ON filter_dc.document_id = d.id"
            filters.append("filter_dc.collection_id = ?")
            params.append(collection_id)
        if search_query:
            filters.append("(LOWER(d.title) LIKE ? OR LOWER(COALESCE(d.filename, '')) LIKE ?)")
            like_query = f"%{search_query.lower()}%"
            params.extend([like_query, like_query])
        where_clause = " AND ".join(filters)
        with get_connection() as connection:
            rows = connection.execute(
                f"""
                SELECT d.*,
                    (SELECT ia.status FROM ingestion_attempts ia WHERE ia.document_id = d.id ORDER BY ia.created_at DESC LIMIT 1) AS latest_status,
                    (SELECT ia.duplicate_status FROM ingestion_attempts ia WHERE ia.document_id = d.id ORDER BY ia.created_at DESC LIMIT 1) AS latest_duplicate_status,
                    (SELECT COUNT(*) FROM chunks c WHERE c.document_id = d.id) AS chunk_count
                FROM documents d {join_clause}
                WHERE {where_clause}
                ORDER BY d.created_at DESC
                """,
                params,
            ).fetchall()
            documents = [dict(row) for row in rows]
            for document in documents:
                collection_rows = connection.execute(
                    """
                    SELECT c.id, c.name FROM collections c
                    JOIN document_collections dc ON dc.collection_id = c.id
                    WHERE dc.document_id = ? AND c.deleted_at IS NULL
                    ORDER BY c.name
                    """,
                    (document["id"],),
                ).fetchall()
                document["metadata"] = json.loads(document.pop("metadata_json"))
                document["collections"] = [dict(item) for item in collection_rows]
        return documents

    def list_all_documents_for_duplicate_detection(self) -> list[dict[str, Any]]:
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM documents WHERE deleted_at IS NULL ORDER BY created_at ASC"
            ).fetchall()
        records = []
        for row in rows:
            record = dict(row)
            record["metadata"] = json.loads(record.pop("metadata_json"))
            records.append(record)
        return records

    def assign_document_to_collections(self, document_id: str, collection_ids: list[str]) -> None:
        now = _utc_now()
        with get_connection() as connection:
            connection.execute("DELETE FROM document_collections WHERE document_id = ?", (document_id,))
            for collection_id in collection_ids:
                connection.execute(
                    "INSERT INTO document_collections(document_id, collection_id, created_at) VALUES (?, ?, ?)",
                    (document_id, collection_id, now),
                )
            self._create_lifecycle_event(
                connection,
                document_id=document_id,
                ingestion_attempt_id=None,
                event_type="document_collections_updated",
                from_status=None,
                to_status=None,
                details={"collection_ids": collection_ids},
            )

    def delete_document(self, document_id: str) -> bool:
        with get_connection() as connection:
            connection.execute(
                "UPDATE documents SET version_of_document_id = NULL WHERE version_of_document_id = ?",
                (document_id,),
            )
            row = connection.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            if row.rowcount:
                self._create_lifecycle_event(
                    connection,
                    document_id=None,
                    ingestion_attempt_id=None,
                    event_type="document_deleted",
                    from_status=None,
                    to_status=None,
                    details={"document_id": document_id},
                )
        return row.rowcount > 0

    def record_reindex_request(self, document_id: str) -> None:
        with get_connection() as connection:
            self._create_lifecycle_event(
                connection,
                document_id=document_id,
                ingestion_attempt_id=None,
                event_type="document_reindex_requested",
                from_status=None,
                to_status=None,
                details={},
            )
