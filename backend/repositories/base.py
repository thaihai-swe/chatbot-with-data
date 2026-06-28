from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime
from typing import Any

from database import get_connection


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


class BaseRepository:
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
