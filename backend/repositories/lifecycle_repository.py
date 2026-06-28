from __future__ import annotations

import json
import uuid
from typing import Any

from database import get_connection
from repositories.base import BaseRepository


class LifecycleRepository(BaseRepository):
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
                    "SELECT * FROM lifecycle_events WHERE ingestion_attempt_id = ? ORDER BY created_at ASC",
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
                (decision_id, ingestion_attempt_id, document_id, matched_document_id, classification, detection_method, json.dumps(evidence), action, final_status),
            )
        return self.get_duplicate_decision(decision_id)

    def get_duplicate_decision(self, decision_id: str) -> dict[str, Any] | None:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM duplicate_decisions WHERE id = ?", (decision_id,)
            ).fetchone()
        if not row:
            return None
        record = dict(row)
        record["evidence"] = json.loads(record.pop("evidence_json"))
        return record

    def list_duplicate_decisions_for_attempt(self, ingestion_attempt_id: str) -> list[dict[str, Any]]:
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM duplicate_decisions WHERE ingestion_attempt_id = ? ORDER BY created_at ASC",
                (ingestion_attempt_id,),
            ).fetchall()
        decisions = []
        for row in rows:
            record = dict(row)
            record["evidence"] = json.loads(record.pop("evidence_json"))
            decisions.append(record)
        return decisions

    def get_latest_duplicate_decision_for_attempt(self, ingestion_attempt_id: str) -> dict[str, Any] | None:
        decisions = self.list_duplicate_decisions_for_attempt(ingestion_attempt_id)
        return decisions[-1] if decisions else None
