from backend.persistence.db import get_connection
from backend.utils import generate_id, utcnow_iso


class CollectionService:
    def __init__(self, sqlite_path):
        self.sqlite_path = sqlite_path

    def create_collection(self, name, description=None, routing_description=None):
        now = utcnow_iso()
        collection_id = generate_id("col")
        with get_connection(self.sqlite_path) as connection:
            connection.execute(
                """
                INSERT INTO collections (
                    collection_id, name, description, routing_description, is_default, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    collection_id,
                    name,
                    description,
                    routing_description,
                    0,
                    now,
                    now,
                ),
            )
        return self.get_collection(collection_id)

    def list_collections(self):
        with get_connection(self.sqlite_path) as connection:
            rows = connection.execute(
                """
                SELECT
                    c.collection_id,
                    c.name,
                    c.description,
                    c.routing_description,
                    c.is_default,
                    c.created_at,
                    c.updated_at,
                    COUNT(DISTINCT d.document_id) AS document_count,
                    COUNT(DISTINCT cm.chunk_id) AS chunk_count
                FROM collections c
                LEFT JOIN documents d
                    ON d.collection_id = c.collection_id
                    AND d.deletion_state = 'active'
                    AND d.ingestion_status != 'skipped'
                LEFT JOIN chunk_metadata cm
                    ON cm.collection_id = c.collection_id
                GROUP BY c.collection_id
                ORDER BY c.created_at ASC
                """
            ).fetchall()
        return rows

    def get_collection(self, collection_id):
        with get_connection(self.sqlite_path) as connection:
            row = connection.execute(
                """
                SELECT
                    c.collection_id,
                    c.name,
                    c.description,
                    c.routing_description,
                    c.is_default,
                    c.created_at,
                    c.updated_at,
                    COUNT(DISTINCT d.document_id) AS document_count,
                    COUNT(DISTINCT cm.chunk_id) AS chunk_count
                FROM collections c
                LEFT JOIN documents d
                    ON d.collection_id = c.collection_id
                    AND d.deletion_state = 'active'
                    AND d.ingestion_status != 'skipped'
                LEFT JOIN chunk_metadata cm
                    ON cm.collection_id = c.collection_id
                WHERE c.collection_id = ?
                GROUP BY c.collection_id
                """,
                (collection_id,),
            ).fetchone()
        return row

    def update_collection(self, collection_id, name=None, description=None, routing_description=None):
        current = self.get_collection(collection_id)
        if not current:
            return None

        now = utcnow_iso()
        with get_connection(self.sqlite_path) as connection:
            connection.execute(
                """
                UPDATE collections
                SET name = ?, description = ?, routing_description = ?, updated_at = ?
                WHERE collection_id = ?
                """,
                (
                    name if name is not None else current["name"],
                    description if description is not None else current["description"],
                    routing_description
                    if routing_description is not None
                    else current["routing_description"],
                    now,
                    collection_id,
                ),
            )
        return self.get_collection(collection_id)

    def set_default_collection(self, collection_id):
        if not self.get_collection(collection_id):
            return None
        now = utcnow_iso()
        with get_connection(self.sqlite_path) as connection:
            connection.execute("UPDATE collections SET is_default = 0, updated_at = ?", (now,))
            connection.execute(
                "UPDATE collections SET is_default = 1, updated_at = ? WHERE collection_id = ?",
                (now, collection_id),
            )
        return self.get_collection(collection_id)

    def delete_collection(self, collection_id):
        collection = self.get_collection(collection_id)
        if not collection:
            return False, "Collection not found"
        if collection["document_count"] > 0:
            return False, "Collection must be empty before deletion"
        with get_connection(self.sqlite_path) as connection:
            connection.execute("DELETE FROM collections WHERE collection_id = ?", (collection_id,))
        return True, None
