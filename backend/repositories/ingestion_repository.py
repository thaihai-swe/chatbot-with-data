from __future__ import annotations

import json
import uuid
from typing import Any

from database import get_connection
from repositories.base import BaseRepository, _utc_now


class IngestionRepository(BaseRepository):
    def create_ingestion_attempt(
        self,
        *,
        source_type: str,
        status: str,
        submitted_filename: str | None = None,
        source_uri: str | None = None,
        mime_type: str | None = None,
        artifact_path: str | None = None,
        collection_ids: list[str] | None = None,
        document_id: str | None = None,
    ) -> dict[str, Any]:
        attempt_id = str(uuid.uuid4())
        now = _utc_now()
        collection_ids = collection_ids or []
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO ingestion_attempts(
                    id, document_id, source_type, status, submitted_filename, source_uri, mime_type,
                    artifact_path, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (attempt_id, document_id, source_type, status, submitted_filename, source_uri, mime_type, artifact_path, now, now),
            )
            for collection_id in collection_ids:
                connection.execute(
                    "INSERT OR IGNORE INTO ingestion_attempt_collections(ingestion_attempt_id, collection_id, created_at) VALUES (?, ?, ?)",
                    (attempt_id, collection_id, now),
                )
            self._create_lifecycle_event(
                connection,
                document_id=document_id,
                ingestion_attempt_id=attempt_id,
                event_type="ingestion_submitted",
                from_status=None,
                to_status=status,
                details={},
            )
        return self.get_ingestion_attempt(attempt_id)

    def update_ingestion_attempt(
        self,
        attempt_id: str,
        *,
        status: str | None = None,
        document_id: str | None = None,
        title: str | None = None,
        extracted_text: str | None = None,
        metadata: dict[str, Any] | None = None,
        source_uri: str | None = None,
        canonical_source_uri: str | None = None,
        snapshot_path: str | None = None,
        file_hash: str | None = None,
        normalized_text_hash: str | None = None,
        duplicate_status: str | None = None,
        duplicate_match_document_id: str | None = None,
        duplicate_evidence: dict[str, Any] | None = None,
        error_message: str | None = None,
        completed: bool = False,
    ) -> dict[str, Any]:
        current = self.get_ingestion_attempt(attempt_id)
        if not current:
            raise KeyError(f"Ingestion attempt {attempt_id} not found")
        next_status = status or current["status"]
        update_values = {
            "document_id": document_id if document_id is not None else current["document_id"],
            "status": next_status,
            "title": title if title is not None else current["title"],
            "extracted_text": extracted_text if extracted_text is not None else current["extracted_text"],
            "metadata_json": json.dumps(metadata if metadata is not None else json.loads(current["metadata_json"])),
            "source_uri": source_uri if source_uri is not None else current["source_uri"],
            "canonical_source_uri": canonical_source_uri if canonical_source_uri is not None else current["canonical_source_uri"],
            "snapshot_path": snapshot_path if snapshot_path is not None else current["snapshot_path"],
            "file_hash": file_hash if file_hash is not None else current["file_hash"],
            "normalized_text_hash": normalized_text_hash if normalized_text_hash is not None else current["normalized_text_hash"],
            "duplicate_status": duplicate_status if duplicate_status is not None else current["duplicate_status"],
            "duplicate_match_document_id": duplicate_match_document_id if duplicate_match_document_id is not None else current["duplicate_match_document_id"],
            "duplicate_evidence_json": (
                json.dumps(duplicate_evidence)
                if duplicate_evidence is not None
                else (
                    current["duplicate_evidence_json"]
                    if current["duplicate_evidence_json"]
                    else None
                )
            ) if duplicate_evidence is not None or current["duplicate_evidence_json"] is not None else None,
            "error_message": error_message if error_message is not None else current["error_message"],
            "updated_at": _utc_now(),
            "completed_at": _utc_now() if completed else current["completed_at"],
        }
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE ingestion_attempts
                SET document_id = ?, status = ?, title = ?, extracted_text = ?, metadata_json = ?,
                    source_uri = ?, canonical_source_uri = ?, snapshot_path = ?, file_hash = ?,
                    normalized_text_hash = ?, duplicate_status = ?, duplicate_match_document_id = ?,
                    duplicate_evidence_json = ?, error_message = ?, updated_at = ?, completed_at = ?
                WHERE id = ?
                """,
                (
                    update_values["document_id"], update_values["status"], update_values["title"],
                    update_values["extracted_text"], update_values["metadata_json"],
                    update_values["source_uri"], update_values["canonical_source_uri"],
                    update_values["snapshot_path"], update_values["file_hash"],
                    update_values["normalized_text_hash"], update_values["duplicate_status"],
                    update_values["duplicate_match_document_id"], update_values["duplicate_evidence_json"],
                    update_values["error_message"], update_values["updated_at"], update_values["completed_at"],
                    attempt_id,
                ),
            )
            if status and status != current["status"]:
                self._create_lifecycle_event(
                    connection,
                    document_id=update_values["document_id"],
                    ingestion_attempt_id=attempt_id,
                    event_type="ingestion_status_changed",
                    from_status=current["status"],
                    to_status=status,
                    details={"error_message": error_message},
                )
        return self.get_ingestion_attempt(attempt_id)

    def get_ingestion_attempt(self, attempt_id: str) -> dict[str, Any] | None:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM ingestion_attempts WHERE id = ?", (attempt_id,)
            ).fetchone()
            if not row:
                return None
            collections = connection.execute(
                """
                SELECT collection_id FROM ingestion_attempt_collections
                WHERE ingestion_attempt_id = ? ORDER BY collection_id
                """,
                (attempt_id,),
            ).fetchall()
        record = dict(row)
        record["collection_ids"] = [item["collection_id"] for item in collections]
        return record

    def list_ingestion_attempts(self, *, status: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM ingestion_attempts"
        params: list[Any] = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC"
        with get_connection() as connection:
            rows = connection.execute(query, params).fetchall()
            collection_rows = connection.execute(
                "SELECT ingestion_attempt_id, collection_id FROM ingestion_attempt_collections"
            ).fetchall()
        collections_by_attempt: dict[str, list[str]] = {}
        for row in collection_rows:
            collections_by_attempt.setdefault(row["ingestion_attempt_id"], []).append(row["collection_id"])
        attempts = []
        for row in rows:
            record = dict(row)
            record["collection_ids"] = collections_by_attempt.get(record["id"], [])
            attempts.append(record)
        return attempts

    def create_reingest_attempt(
        self,
        *,
        document_id: str,
        collection_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        from repositories.document_repository import DocumentRepository
        doc_repo = DocumentRepository()
        document = doc_repo.get_document(document_id)
        if not document:
            raise KeyError(f"Document {document_id} not found")
        collection_ids = collection_ids or [item["id"] for item in document["collections"]]
        attempt = self.create_ingestion_attempt(
            source_type=document["source_type"],
            status="submitted",
            submitted_filename=document["filename"],
            source_uri=document["source_uri"],
            mime_type=document["mime_type"],
            artifact_path=None,
            collection_ids=collection_ids,
            document_id=document_id,
        )
        with get_connection() as connection:
            self._create_lifecycle_event(
                connection,
                document_id=document_id,
                ingestion_attempt_id=attempt["id"],
                event_type="document_reingest_requested",
                from_status=None,
                to_status="submitted",
                details={"collection_ids": collection_ids},
            )
        return attempt
