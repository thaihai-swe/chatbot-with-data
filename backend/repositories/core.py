from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime
from typing import Any

from database import get_connection


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


class Repository:
    def create_collection(
        self,
        *,
        name: str,
        description: str | None = None,
        is_default: bool = False,
        routing_enabled: bool = False,
    ) -> dict[str, Any]:
        collection_id = str(uuid.uuid4())
        now = _utc_now()
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO collections(id, name, description, is_default, routing_enabled, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    collection_id,
                    name,
                    description,
                    int(is_default),
                    int(routing_enabled),
                    now,
                    now,
                ),
            )
        return self.get_collection(collection_id)

    def list_collections(self) -> list[dict[str, Any]]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT c.*,
                       COUNT(DISTINCT dc.document_id) AS document_count
                FROM collections c
                LEFT JOIN document_collections dc ON dc.collection_id = c.id
                WHERE c.deleted_at IS NULL
                GROUP BY c.id
                ORDER BY c.created_at ASC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_collection_members(self, collection_id: str) -> list[dict[str, Any]]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT d.*
                FROM documents d
                JOIN document_collections dc ON dc.document_id = d.id
                WHERE dc.collection_id = ? AND d.deleted_at IS NULL
                ORDER BY d.created_at DESC
                """,
                (collection_id,),
            ).fetchall()
        members = []
        for row in rows:
            record = dict(row)
            record["metadata"] = json.loads(record.pop("metadata_json"))
            members.append(record)
        return members

    def get_collection(self, collection_id: str) -> dict[str, Any] | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT c.*,
                       COUNT(DISTINCT dc.document_id) AS document_count
                FROM collections c
                LEFT JOIN document_collections dc ON dc.collection_id = c.id
                WHERE c.id = ? AND c.deleted_at IS NULL
                GROUP BY c.id
                """,
                (collection_id,),
            ).fetchone()
        return dict(row) if row else None

    def update_collection(
        self,
        collection_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        is_default: bool | None = None,
        routing_enabled: bool | None = None,
    ) -> dict[str, Any] | None:
        current = self.get_collection(collection_id)
        if not current:
            return None
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE collections
                SET name = ?, description = ?, is_default = ?, routing_enabled = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    name if name is not None else current["name"],
                    description if description is not None else current["description"],
                    int(is_default) if is_default is not None else current["is_default"],
                    int(routing_enabled)
                    if routing_enabled is not None
                    else current["routing_enabled"],
                    _utc_now(),
                    collection_id,
                ),
            )
        return self.get_collection(collection_id)

    def delete_collection(self, collection_id: str) -> bool:
        with get_connection() as connection:
            row = connection.execute(
                "UPDATE collections SET deleted_at = ?, updated_at = ? WHERE id = ? AND deleted_at IS NULL",
                (_utc_now(), _utc_now(), collection_id),
            )
        return row.rowcount > 0

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
                (
                    attempt_id,
                    document_id,
                    source_type,
                    status,
                    submitted_filename,
                    source_uri,
                    mime_type,
                    artifact_path,
                    now,
                    now,
                ),
            )
            for collection_id in collection_ids:
                connection.execute(
                    """
                    INSERT OR IGNORE INTO ingestion_attempt_collections(ingestion_attempt_id, collection_id, created_at)
                    VALUES (?, ?, ?)
                    """,
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
            "extracted_text": extracted_text
            if extracted_text is not None
            else current["extracted_text"],
            "metadata_json": json.dumps(
                metadata if metadata is not None else json.loads(current["metadata_json"])
            ),
            "source_uri": source_uri if source_uri is not None else current["source_uri"],
            "canonical_source_uri": canonical_source_uri
            if canonical_source_uri is not None
            else current["canonical_source_uri"],
            "snapshot_path": snapshot_path
            if snapshot_path is not None
            else current["snapshot_path"],
            "file_hash": file_hash if file_hash is not None else current["file_hash"],
            "normalized_text_hash": normalized_text_hash
            if normalized_text_hash is not None
            else current["normalized_text_hash"],
            "duplicate_status": duplicate_status
            if duplicate_status is not None
            else current["duplicate_status"],
            "duplicate_match_document_id": duplicate_match_document_id
            if duplicate_match_document_id is not None
            else current["duplicate_match_document_id"],
            "duplicate_evidence_json": json.dumps(
                duplicate_evidence
                if duplicate_evidence is not None
                else (
                    json.loads(current["duplicate_evidence_json"])
                    if current["duplicate_evidence_json"]
                    else None
                )
            )
            if duplicate_evidence is not None or current["duplicate_evidence_json"] is not None
            else None,
            "error_message": error_message
            if error_message is not None
            else current["error_message"],
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
                    update_values["document_id"],
                    update_values["status"],
                    update_values["title"],
                    update_values["extracted_text"],
                    update_values["metadata_json"],
                    update_values["source_uri"],
                    update_values["canonical_source_uri"],
                    update_values["snapshot_path"],
                    update_values["file_hash"],
                    update_values["normalized_text_hash"],
                    update_values["duplicate_status"],
                    update_values["duplicate_match_document_id"],
                    update_values["duplicate_evidence_json"],
                    update_values["error_message"],
                    update_values["updated_at"],
                    update_values["completed_at"],
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
                "SELECT * FROM ingestion_attempts WHERE id = ?",
                (attempt_id,),
            ).fetchone()
            if not row:
                return None
            collections = connection.execute(
                """
                SELECT collection_id
                FROM ingestion_attempt_collections
                WHERE ingestion_attempt_id = ?
                ORDER BY collection_id
                """,
                (attempt_id,),
            ).fetchall()
        record = dict(row)
        record["collection_ids"] = [item["collection_id"] for item in collections]
        return record

    def list_ingestion_attempts(
        self,
        *,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
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
            collections_by_attempt.setdefault(row["ingestion_attempt_id"], []).append(
                row["collection_id"]
            )
        attempts = []
        for row in rows:
            record = dict(row)
            record["collection_ids"] = collections_by_attempt.get(record["id"], [])
            attempts.append(record)
        return attempts

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
                    document_id,
                    title,
                    source_type,
                    source_uri,
                    canonical_source_uri,
                    filename,
                    mime_type,
                    file_hash,
                    normalized_text_hash,
                    extracted_text,
                    json.dumps(metadata),
                    version_of_document_id,
                    now,
                    now,
                ),
            )
            for collection_id in collection_ids:
                connection.execute(
                    """
                    INSERT OR IGNORE INTO document_collections(document_id, collection_id, created_at)
                    VALUES (?, ?, ?)
                    """,
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
                    canonical_source_uri
                    if canonical_source_uri is not None
                    else current["canonical_source_uri"],
                    filename if filename is not None else current["filename"],
                    mime_type if mime_type is not None else current["mime_type"],
                    file_hash if file_hash is not None else current["file_hash"],
                    normalized_text_hash
                    if normalized_text_hash is not None
                    else current["normalized_text_hash"],
                    extracted_text
                    if extracted_text is not None
                    else current["extracted_text"],
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
                SELECT c.id, c.name
                FROM collections c
                JOIN document_collections dc ON dc.collection_id = c.id
                WHERE dc.document_id = ? AND c.deleted_at IS NULL
                ORDER BY c.name
                """,
                (document_id,),
            ).fetchall()
            latest_attempt = connection.execute(
                """
                SELECT *
                FROM ingestion_attempts
                WHERE document_id = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (document_id,),
            ).fetchone()
        record = dict(row)
        record["metadata"] = json.loads(record.pop("metadata_json"))
        record["collections"] = [dict(item) for item in collection_rows]
        record["latest_attempt"] = dict(latest_attempt) if latest_attempt else None
        return record

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
                       (
                           SELECT ia.status
                           FROM ingestion_attempts ia
                           WHERE ia.document_id = d.id
                           ORDER BY ia.created_at DESC
                           LIMIT 1
                       ) AS latest_status,
                       (
                           SELECT ia.duplicate_status
                           FROM ingestion_attempts ia
                           WHERE ia.document_id = d.id
                           ORDER BY ia.created_at DESC
                           LIMIT 1
                       ) AS latest_duplicate_status
                FROM documents d
                {join_clause}
                WHERE {where_clause}
                ORDER BY d.created_at DESC
                """,
                params,
            ).fetchall()
            documents = [dict(row) for row in rows]
            for document in documents:
                collection_rows = connection.execute(
                    """
                    SELECT c.id, c.name
                    FROM collections c
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

    def assign_document_to_collections(
        self, document_id: str, collection_ids: list[str]
    ) -> None:
        now = _utc_now()
        with get_connection() as connection:
            connection.execute(
                "DELETE FROM document_collections WHERE document_id = ?",
                (document_id,),
            )
            for collection_id in collection_ids:
                connection.execute(
                    """
                    INSERT INTO document_collections(document_id, collection_id, created_at)
                    VALUES (?, ?, ?)
                    """,
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
            row = connection.execute(
                "DELETE FROM documents WHERE id = ?",
                (document_id,),
            )
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

    def create_duplicate_decision(
        self,
        *,
        ingestion_attempt_id: str,
        document_id: str | None,
        matched_document_id: str | None,
        classification: str,
        detection_method: str,
        evidence: dict[str, Any],
        action: str,
        final_status: str,
    ) -> dict[str, Any]:
        decision_id = str(uuid.uuid4())
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO duplicate_decisions(
                    id, ingestion_attempt_id, document_id, matched_document_id, classification,
                    detection_method, evidence_json, action, final_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision_id,
                    ingestion_attempt_id,
                    document_id,
                    matched_document_id,
                    classification,
                    detection_method,
                    json.dumps(evidence),
                    action,
                    final_status,
                ),
            )
        return self.get_duplicate_decision(decision_id)

    def get_duplicate_decision(self, decision_id: str) -> dict[str, Any] | None:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM duplicate_decisions WHERE id = ?",
                (decision_id,),
            ).fetchone()
        if not row:
            return None
        record = dict(row)
        record["evidence"] = json.loads(record.pop("evidence_json"))
        return record

    def list_duplicate_decisions_for_attempt(
        self, ingestion_attempt_id: str
    ) -> list[dict[str, Any]]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM duplicate_decisions
                WHERE ingestion_attempt_id = ?
                ORDER BY created_at ASC
                """,
                (ingestion_attempt_id,),
            ).fetchall()
        decisions: list[dict[str, Any]] = []
        for row in rows:
            record = dict(row)
            record["evidence"] = json.loads(record.pop("evidence_json"))
            decisions.append(record)
        return decisions

    def get_latest_duplicate_decision_for_attempt(
        self, ingestion_attempt_id: str
    ) -> dict[str, Any] | None:
        decisions = self.list_duplicate_decisions_for_attempt(ingestion_attempt_id)
        return decisions[-1] if decisions else None

    def create_reingest_attempt(
        self,
        *,
        document_id: str,
        collection_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        document = self.get_document(document_id)
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

    def list_lifecycle_events(
        self,
        *,
        document_id: str | None = None,
        ingestion_attempt_id: str | None = None,
    ) -> list[dict[str, Any]]:
        with get_connection() as connection:
            if document_id:
                rows = connection.execute(
                    "SELECT * FROM lifecycle_events WHERE document_id = ? ORDER BY created_at ASC",
                    (document_id,),
                ).fetchall()
            elif ingestion_attempt_id:
                rows = connection.execute(
                    """
                    SELECT * FROM lifecycle_events
                    WHERE ingestion_attempt_id = ?
                    ORDER BY created_at ASC
                    """,
                    (ingestion_attempt_id,),
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM lifecycle_events ORDER BY created_at ASC"
                ).fetchall()
        events = []
        for row in rows:
            record = dict(row)
            record["details"] = json.loads(record.pop("details_json"))
            events.append(record)
        return events

    def _create_lifecycle_event(
        self,
        connection: sqlite3.Connection,
        *,
        document_id: str | None,
        ingestion_attempt_id: str | None,
        event_type: str,
        from_status: str | None,
        to_status: str | None,
        details: dict[str, Any],
    ) -> None:
        connection.execute(
            """
            INSERT INTO lifecycle_events(
                id, document_id, ingestion_attempt_id, event_type, from_status, to_status, details_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                document_id,
                ingestion_attempt_id,
                event_type,
                from_status,
                to_status,
                json.dumps(details),
            ),
        )
