"""Repository for index generation records."""
from __future__ import annotations

from typing import Optional

from database import get_connection
from models.enums import IndexGenerationStatus
from models.index_generation import IndexGeneration


class IndexGenerationRepository:
    """Repository for managing index generation records."""

    @staticmethod
    def create_generation(
        id: str,
        document_id: str,
        generation_number: int,
        status: IndexGenerationStatus,
        strategy: str,
        chunk_count: int,
        settings_hash: Optional[str] = None,
        embedding_model: Optional[str] = None,
    ) -> IndexGeneration:
        """Create a new index generation record."""
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO index_generations
                (id, document_id, generation_number, status, strategy, chunk_count, settings_hash, embedding_model)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    id,
                    document_id,
                    generation_number,
                    status.value,
                    strategy,
                    chunk_count,
                    settings_hash,
                    embedding_model,
                ),
            )

        return IndexGenerationRepository.get_generation(id)

    @staticmethod
    def get_generation(generation_id: str) -> Optional[IndexGeneration]:
        """Get a generation by ID."""
        with get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, document_id, generation_number, status, strategy,
                       chunk_count, is_active, settings_hash, embedding_model, created_at, completed_at
                FROM index_generations
                WHERE id = ?
                """,
                (generation_id,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        return IndexGeneration(
            id=row[0],
            document_id=row[1],
            generation_number=row[2],
            status=IndexGenerationStatus(row[3]),
            strategy=row[4],
            chunk_count=row[5],
            is_active=bool(row[6]),
            settings_hash=row[7],
            embedding_model=row[8],
            created_at=row[9],
            completed_at=row[10],
        )

    @staticmethod
    def list_generations_by_document(document_id: str) -> list[IndexGeneration]:
        """List all generations for a document."""
        with get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, document_id, generation_number, status, strategy,
                       chunk_count, is_active, settings_hash, embedding_model, created_at, completed_at
                FROM index_generations
                WHERE document_id = ?
                ORDER BY generation_number DESC
                """,
                (document_id,),
            )
            rows = cursor.fetchall()

        return [
            IndexGeneration(
                id=row[0],
                document_id=row[1],
                generation_number=row[2],
                status=IndexGenerationStatus(row[3]),
                strategy=row[4],
                chunk_count=row[5],
                is_active=bool(row[6]),
                settings_hash=row[7],
                embedding_model=row[8],
                created_at=row[9],
                completed_at=row[10],
            )
            for row in rows
        ]

    @staticmethod
    def get_active_generation(document_id: str) -> Optional[IndexGeneration]:
        """Get the active generation for a document."""
        with get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, document_id, generation_number, status, strategy,
                       chunk_count, is_active, settings_hash, embedding_model, created_at, completed_at
                FROM index_generations
                WHERE document_id = ? AND is_active = 1
                """,
                (document_id,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        return IndexGeneration(
            id=row[0],
            document_id=row[1],
            generation_number=row[2],
            status=IndexGenerationStatus(row[3]),
            strategy=row[4],
            chunk_count=row[5],
            is_active=bool(row[6]),
            settings_hash=row[7],
            embedding_model=row[8],
            created_at=row[9],
            completed_at=row[10],
        )

    @staticmethod
    def update_status(
        generation_id: str, status: IndexGenerationStatus, completed_at: Optional[str] = None
    ) -> IndexGeneration:
        """Update generation status."""
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE index_generations
                SET status = ?, completed_at = ?
                WHERE id = ?
                """,
                (status.value, completed_at, generation_id),
            )

        return IndexGenerationRepository.get_generation(generation_id)

    @staticmethod
    def mark_active(generation_id: str) -> IndexGeneration:
        """Mark a generation as active and deactivate all other generations for the same document."""
        # Get the document_id first
        with get_connection() as connection:
            cursor = connection.execute(
                "SELECT document_id FROM index_generations WHERE id = ?",
                (generation_id,),
            )
            row = cursor.fetchone()

        if not row:
            raise ValueError(f"Generation {generation_id} not found")

        document_id = row[0]

        # Deactivate all generations for this document
        with get_connection() as connection:
            connection.execute(
                "UPDATE index_generations SET is_active = 0 WHERE document_id = ?",
                (document_id,),
            )

            # Activate the specified generation
            connection.execute(
                "UPDATE index_generations SET is_active = 1 WHERE id = ?",
                (generation_id,),
            )

        return IndexGenerationRepository.get_generation(generation_id)

    @staticmethod
    def mark_inactive(generation_id: str) -> IndexGeneration:
        """Mark a generation as inactive."""
        with get_connection() as connection:
            connection.execute(
                "UPDATE index_generations SET is_active = 0 WHERE id = ?",
                (generation_id,),
            )

        return IndexGenerationRepository.get_generation(generation_id)

    @staticmethod
    def delete_generation(generation_id: str) -> None:
        """Delete a generation (and all associated index entries via cascade)."""
        with get_connection() as connection:
            connection.execute(
                "DELETE FROM index_generations WHERE id = ?",
                (generation_id,),
            )

    @staticmethod
    def delete_generations_by_document(document_id: str) -> None:
        """Delete all generations for a document (and all associated index entries via cascade)."""
        with get_connection() as connection:
            connection.execute(
                "DELETE FROM index_generations WHERE document_id = ?",
                (document_id,),
            )

    @staticmethod
    def count_generations_by_document(document_id: str) -> int:
        """Count total generations for a document."""
        with get_connection() as connection:
            cursor = connection.execute(
                "SELECT COUNT(*) FROM index_generations WHERE document_id = ?",
                (document_id,),
            )
            return cursor.fetchone()[0]
