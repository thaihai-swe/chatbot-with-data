from __future__ import annotations

import json
import uuid
from typing import Any

from database import get_connection
from repositories.base import BaseRepository, _utc_now


class CollectionRepository(BaseRepository):
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
                (collection_id, name, description, int(is_default), int(routing_enabled), now, now),
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
                    int(routing_enabled) if routing_enabled is not None else current["routing_enabled"],
                    _utc_now(),
                    collection_id,
                ),
            )
        return self.get_collection(collection_id)

    def get_or_create_default(self) -> dict[str, Any]:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM collections WHERE is_default = 1 AND deleted_at IS NULL LIMIT 1"
            ).fetchone()
            if row:
                return dict(row)
        return self.create_collection(name="Default", description="Default collection", is_default=True)

    def delete_collection(self, collection_id: str) -> bool:
        with get_connection() as connection:
            row = connection.execute(
                "UPDATE collections SET deleted_at = ?, updated_at = ? WHERE id = ? AND deleted_at IS NULL",
                (_utc_now(), _utc_now(), collection_id),
            )
        return row.rowcount > 0
