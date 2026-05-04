from backend.persistence.db import get_connection
from backend.utils import generate_id, utcnow_iso


class DocumentService:
    def __init__(self, sqlite_path):
        self.sqlite_path = sqlite_path

    def create_document(
        self,
        source_type,
        collection_id=None,
        source_path=None,
        source_url=None,
        source_identity=None,
        source_filename=None,
        title=None,
        raw_text=None,
        ingestion_status="pending",
        duplicate_status=None,
        file_hash=None,
        text_hash=None,
        freshness_metadata=None,
    ):
        now = utcnow_iso()
        document_id = generate_id("doc")
        with get_connection(self.sqlite_path) as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    document_id, collection_id, source_type, source_path, source_url,
                    source_identity, source_filename, title, raw_text, ingestion_status,
                    duplicate_status, deletion_state, file_hash, text_hash,
                    freshness_metadata, created_at, last_indexed_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    collection_id,
                    source_type,
                    source_path,
                    source_url,
                    source_identity,
                    source_filename,
                    title,
                    raw_text,
                    ingestion_status,
                    duplicate_status,
                    file_hash,
                    text_hash,
                    freshness_metadata,
                    now,
                    None,
                    now,
                ),
            )
        return self.get_document(document_id)

    def get_document(self, document_id):
        with get_connection(self.sqlite_path) as connection:
            row = connection.execute(
                """
                SELECT
                    d.*,
                    c.name AS collection_name,
                    COUNT(DISTINCT cm.chunk_id) AS chunk_count
                FROM documents d
                LEFT JOIN collections c ON c.collection_id = d.collection_id
                LEFT JOIN chunk_metadata cm ON cm.document_id = d.document_id
                WHERE d.document_id = ?
                GROUP BY d.document_id
                """,
                (document_id,),
            ).fetchone()
        return row

    def list_documents(self, collection_id=None, search=None, status=None):
        sql = """
            SELECT
                d.*,
                c.name AS collection_name,
                COUNT(DISTINCT cm.chunk_id) AS chunk_count
            FROM documents d
            LEFT JOIN collections c ON c.collection_id = d.collection_id
            LEFT JOIN chunk_metadata cm ON cm.document_id = d.document_id
            WHERE d.deletion_state = 'active'
        """
        params = []

        if collection_id:
            sql += " AND d.collection_id = ?"
            params.append(collection_id)
        if status:
            sql += " AND d.ingestion_status = ?"
            params.append(status)
        if search:
            sql += " AND LOWER(COALESCE(d.title, '')) LIKE ?"
            params.append(f"%{search.lower()}%")

        sql += " GROUP BY d.document_id ORDER BY d.created_at DESC"

        with get_connection(self.sqlite_path) as connection:
            rows = connection.execute(sql, params).fetchall()
        return rows

    def list_documents_for_collection(self, collection_id):
        return self.list_documents(collection_id=collection_id)

    def update_document(self, document_id, **fields):
        current = self.get_document(document_id)
        if not current:
            return None

        assignments = []
        values = []
        for key, value in fields.items():
            assignments.append(f"{key} = ?")
            values.append(value)
        assignments.append("updated_at = ?")
        values.append(utcnow_iso())
        values.append(document_id)

        with get_connection(self.sqlite_path) as connection:
            connection.execute(
                f"UPDATE documents SET {', '.join(assignments)} WHERE document_id = ?",
                values,
            )
        return self.get_document(document_id)

    def move_document_to_collection(self, document_id, collection_id):
        return self.update_document(document_id, collection_id=collection_id)

    def mark_last_indexed(self, document_id):
        return self.update_document(document_id, last_indexed_at=utcnow_iso())

    def delete_document_record(self, document_id):
        with get_connection(self.sqlite_path) as connection:
            connection.execute("DELETE FROM duplicate_logs WHERE attempt_id IN (SELECT attempt_id FROM ingestion_attempts WHERE document_id = ?)", (document_id,))
            connection.execute("DELETE FROM ingestion_attempts WHERE document_id = ?", (document_id,))
            connection.execute("DELETE FROM chunk_metadata WHERE document_id = ?", (document_id,))
            connection.execute("DELETE FROM documents WHERE document_id = ?", (document_id,))

    def upsert_chunk_metadata(self, chunk):
        with get_connection(self.sqlite_path) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO chunk_metadata (
                    chunk_id, document_id, collection_id, source_type, title, source_url,
                    section_name, page_number, chunk_order, chunk_text, content_hash,
                    parent_chunk_id, child_chunk_ids_json, semantic_metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk["chunk_id"],
                    chunk["document_id"],
                    chunk.get("collection_id"),
                    chunk["source_type"],
                    chunk.get("title"),
                    chunk.get("source_url"),
                    chunk.get("section_name"),
                    chunk.get("page_number"),
                    chunk["chunk_order"],
                    chunk["chunk_text"],
                    chunk["content_hash"],
                    chunk.get("parent_chunk_id"),
                    chunk.get("child_chunk_ids_json"),
                    chunk.get("semantic_metadata_json"),
                    chunk["created_at"],
                ),
            )

    def replace_chunks(self, document_id, chunks):
        with get_connection(self.sqlite_path) as connection:
            connection.execute("DELETE FROM chunk_metadata WHERE document_id = ?", (document_id,))
        for chunk in chunks:
            self.upsert_chunk_metadata(chunk)

    def get_chunks_for_document(self, document_id):
        with get_connection(self.sqlite_path) as connection:
            rows = connection.execute(
                "SELECT * FROM chunk_metadata WHERE document_id = ? ORDER BY chunk_order ASC",
                (document_id,),
            ).fetchall()
        return rows
