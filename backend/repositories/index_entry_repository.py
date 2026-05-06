"""Repository for index entry records."""
from __future__ import annotations

from typing import Optional

from database import get_connection
from models.index_entry import IndexEntry


class IndexEntryRepository:
    """Repository for managing index entry records."""

    @staticmethod
    def create_entry(
        id: str,
        chunk_id: str,
        embedding_id: str,
        document_id: str,
        collection_id: str,
        generation_id: str,
        chunk_order: int,
        vector_db_id: Optional[str] = None,
        parent_chunk_id: Optional[str] = None,
        is_active: bool = True,
    ) -> IndexEntry:
        """Create a new index entry."""
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO index_entries
                (id, chunk_id, embedding_id, document_id, collection_id, generation_id,
                 chunk_order, vector_db_id, parent_chunk_id, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    id,
                    chunk_id,
                    embedding_id,
                    document_id,
                    collection_id,
                    generation_id,
                    chunk_order,
                    vector_db_id,
                    parent_chunk_id,
                    int(is_active),
                ),
            )

        return IndexEntryRepository.get_entry(id)

    @staticmethod
    def get_entry(entry_id: str) -> Optional[IndexEntry]:
        """Get an index entry by ID."""
        with get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, chunk_id, embedding_id, document_id, collection_id, generation_id,
                       chunk_order, vector_db_id, parent_chunk_id, is_active, created_at
                FROM index_entries
                WHERE id = ?
                """,
                (entry_id,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        return IndexEntry(
            id=row[0],
            chunk_id=row[1],
            embedding_id=row[2],
            document_id=row[3],
            collection_id=row[4],
            generation_id=row[5],
            chunk_order=row[6],
            vector_db_id=row[7],
            parent_chunk_id=row[8],
            is_active=bool(row[9]),
            created_at=row[10],
        )

    @staticmethod
    def list_entries_by_generation(generation_id: str) -> list[IndexEntry]:
        """List all entries for a generation."""
        with get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, chunk_id, embedding_id, document_id, collection_id, generation_id,
                       chunk_order, vector_db_id, parent_chunk_id, is_active, created_at
                FROM index_entries
                WHERE generation_id = ?
                ORDER BY chunk_order
                """,
                (generation_id,),
            )
            rows = cursor.fetchall()

        return [
            IndexEntry(
                id=row[0],
                chunk_id=row[1],
                embedding_id=row[2],
                document_id=row[3],
                collection_id=row[4],
                generation_id=row[5],
                chunk_order=row[6],
                vector_db_id=row[7],
                parent_chunk_id=row[8],
                is_active=bool(row[9]),
                created_at=row[10],
            )
            for row in rows
        ]

    @staticmethod
    def list_entries_by_document(document_id: str, active_only: bool = False) -> list[IndexEntry]:
        """List all entries for a document."""
        query = """
            SELECT id, chunk_id, embedding_id, document_id, collection_id, generation_id,
                   chunk_order, vector_db_id, parent_chunk_id, is_active, created_at
            FROM index_entries
            WHERE document_id = ?
        """
        params = [document_id]

        if active_only:
            query += " AND is_active = 1"

        query += " ORDER BY chunk_order"

        with get_connection() as connection:
            cursor = connection.execute(query, params)
            rows = cursor.fetchall()

        return [
            IndexEntry(
                id=row[0],
                chunk_id=row[1],
                embedding_id=row[2],
                document_id=row[3],
                collection_id=row[4],
                generation_id=row[5],
                chunk_order=row[6],
                vector_db_id=row[7],
                parent_chunk_id=row[8],
                is_active=bool(row[9]),
                created_at=row[10],
            )
            for row in rows
        ]

    @staticmethod
    def list_entries_by_collection(collection_id: str, active_only: bool = False) -> list[IndexEntry]:
        """List all entries for a collection."""
        query = """
            SELECT id, chunk_id, embedding_id, document_id, collection_id, generation_id,
                   chunk_order, vector_db_id, parent_chunk_id, is_active, created_at
            FROM index_entries
            WHERE collection_id = ?
        """
        params = [collection_id]

        if active_only:
            query += " AND is_active = 1"

        query += " ORDER BY chunk_order"

        with get_connection() as connection:
            cursor = connection.execute(query, params)
            rows = cursor.fetchall()

        return [
            IndexEntry(
                id=row[0],
                chunk_id=row[1],
                embedding_id=row[2],
                document_id=row[3],
                collection_id=row[4],
                generation_id=row[5],
                chunk_order=row[6],
                vector_db_id=row[7],
                parent_chunk_id=row[8],
                is_active=bool(row[9]),
                created_at=row[10],
            )
            for row in rows
        ]

    @staticmethod
    def list_entries_by_chunk(chunk_id: str) -> list[IndexEntry]:
        """List all index entries for a chunk."""
        with get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, chunk_id, embedding_id, document_id, collection_id, generation_id,
                       chunk_order, vector_db_id, parent_chunk_id, is_active, created_at
                FROM index_entries
                WHERE chunk_id = ?
                ORDER BY created_at DESC
                """,
                (chunk_id,),
            )
            rows = cursor.fetchall()

        return [
            IndexEntry(
                id=row[0],
                chunk_id=row[1],
                embedding_id=row[2],
                document_id=row[3],
                collection_id=row[4],
                generation_id=row[5],
                chunk_order=row[6],
                vector_db_id=row[7],
                parent_chunk_id=row[8],
                is_active=bool(row[9]),
                created_at=row[10],
            )
            for row in rows
        ]

    @staticmethod
    def update_is_active(entry_id: str, is_active: bool) -> IndexEntry:
        """Update the is_active flag for an entry."""
        with get_connection() as connection:
            connection.execute(
                "UPDATE index_entries SET is_active = ? WHERE id = ?",
                (int(is_active), entry_id),
            )

        return IndexEntryRepository.get_entry(entry_id)

    @staticmethod
    def mark_generation_inactive(generation_id: str) -> None:
        """Mark all entries for a generation as inactive."""
        with get_connection() as connection:
            connection.execute(
                "UPDATE index_entries SET is_active = 0 WHERE generation_id = ?",
                (generation_id,),
            )

    @staticmethod
    def mark_document_entries_active(document_id: str, generation_id: str) -> None:
        """Mark all entries for a document as inactive, then mark entries for a specific generation as active."""
        with get_connection() as connection:
            # Mark all entries for the document as inactive
            connection.execute(
                "UPDATE index_entries SET is_active = 0 WHERE document_id = ?",
                (document_id,),
            )

            # Mark entries for the specified generation as active
            connection.execute(
                "UPDATE index_entries SET is_active = 1 WHERE document_id = ? AND generation_id = ?",
                (document_id, generation_id),
            )

    @staticmethod
    def delete_entry(entry_id: str) -> None:
        """Delete an index entry."""
        with get_connection() as connection:
            connection.execute("DELETE FROM index_entries WHERE id = ?", (entry_id,))

    @staticmethod
    def delete_entries_by_generation(generation_id: str) -> None:
        """Delete all entries for a generation."""
        with get_connection() as connection:
            connection.execute(
                "DELETE FROM index_entries WHERE generation_id = ?",
                (generation_id,),
            )

    @staticmethod
    def delete_entries_by_document(document_id: str) -> None:
        """Delete all entries for a document."""
        with get_connection() as connection:
            connection.execute(
                "DELETE FROM index_entries WHERE document_id = ?",
                (document_id,),
            )

    @staticmethod
    def delete_entries_by_collection(collection_id: str) -> None:
        """Delete all entries for a collection."""
        with get_connection() as connection:
            connection.execute(
                "DELETE FROM index_entries WHERE collection_id = ?",
                (collection_id,),
            )

    @staticmethod
    def count_entries_by_generation(generation_id: str) -> int:
        """Count total entries for a generation."""
        with get_connection() as connection:
            cursor = connection.execute(
                "SELECT COUNT(*) FROM index_entries WHERE generation_id = ?",
                (generation_id,),
            )
            return cursor.fetchone()[0]

    @staticmethod
    def count_entries_by_document(document_id: str, active_only: bool = False) -> int:
        """Count total entries for a document."""
        query = "SELECT COUNT(*) FROM index_entries WHERE document_id = ?"
        params = [document_id]

        if active_only:
            query += " AND is_active = 1"

        with get_connection() as connection:
            cursor = connection.execute(query, params)
            return cursor.fetchone()[0]

    @staticmethod
    def count_entries_by_collection(collection_id: str, active_only: bool = False) -> int:
        """Count total entries for a collection."""
        query = "SELECT COUNT(*) FROM index_entries WHERE collection_id = ?"
        params = [collection_id]

        if active_only:
            query += " AND is_active = 1"

        with get_connection() as connection:
            cursor = connection.execute(query, params)
            return cursor.fetchone()[0]
