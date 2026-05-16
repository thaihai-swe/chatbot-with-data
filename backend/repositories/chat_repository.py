"""Repository for chat sessions, turns, and citations."""
from __future__ import annotations

import json
from typing import Optional, List

from database import get_connection
from models.chat import ChatSession, ChatTurn, Citation


class ChatRepository:
    """Repository for managing chat records."""

    @staticmethod
    def create_session(
        id: str,
        collection_ids: Optional[List[str]] = None,
        metadata_json: str = "{}",
    ) -> ChatSession:
        """Create a new chat session."""
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO chat_sessions (id, metadata_json)
                VALUES (?, ?)
                """,
                (id, metadata_json),
            )
            if collection_ids:
                for col_id in collection_ids:
                    connection.execute(
                        "INSERT INTO chat_session_collections (session_id, collection_id) VALUES (?, ?)",
                        (id, col_id),
                    )
        return ChatRepository.get_session(id)

    @staticmethod
    def get_session(session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID."""
        with get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, created_at, updated_at, metadata_json
                FROM chat_sessions
                WHERE id = ?
                """,
                (session_id,),
            )
            row = cursor.fetchone()

            if not row:
                return None

            # Get collection IDs
            cursor = connection.execute(
                "SELECT collection_id FROM chat_session_collections WHERE session_id = ?",
                (session_id,),
            )
            collection_ids = [r[0] for r in cursor.fetchall()]

        return ChatSession(
            id=row[0],
            collection_ids=collection_ids,
            created_at=row[1],
            updated_at=row[2],
            metadata_json=row[3],
        )

    @staticmethod
    def list_sessions() -> List[ChatSession]:
        """List all chat sessions."""
        with get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT s.id, s.created_at, s.updated_at, s.metadata_json,
                       GROUP_CONCAT(sc.collection_id) as collection_ids
                FROM chat_sessions s
                LEFT JOIN chat_session_collections sc ON s.id = sc.session_id
                GROUP BY s.id
                ORDER BY s.created_at DESC
                """
            )
            rows = cursor.fetchall()

        return [
            ChatSession(
                id=row[0],
                collection_ids=row[4].split(",") if row[4] else [],
                created_at=row[1],
                updated_at=row[2],
                metadata_json=row[3],
            )
            for row in rows
        ]

    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Delete a chat session and its associated data via CASCADE."""
        with get_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM chat_sessions WHERE id = ?",
                (session_id,),
            )
            return cursor.rowcount > 0

    @staticmethod
    def create_turn(
        id: str,
        session_id: str,
        query_text: str,
        answer_text: Optional[str] = None,
        retrieved_chunks_json: str = "[]",
        context_used_json: str = "{}",
        status: str = "pending",
        safety_status: Optional[str] = None,
        safety_risk_score: Optional[float] = None,
        safety_reason: Optional[str] = None,
        groundedness_score: Optional[float] = None,
        error_message: Optional[str] = None,
    ) -> ChatTurn:
        """Create a new chat turn."""
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO chat_turns
                (id, session_id, query_text, answer_text, retrieved_chunks_json,
                 context_used_json, status, safety_status, safety_risk_score,
                 safety_reason, groundedness_score, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    id,
                    session_id,
                    query_text,
                    answer_text,
                    retrieved_chunks_json,
                    context_used_json,
                    status,
                    safety_status,
                    safety_risk_score,
                    safety_reason,
                    groundedness_score,
                    error_message,
                ),
            )
        return ChatRepository.get_turn(id)

    @staticmethod
    def get_turn(turn_id: str) -> Optional[ChatTurn]:
        """Get a chat turn by ID."""
        with get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, session_id, query_text, answer_text, retrieved_chunks_json,
                       context_used_json, status, safety_status, safety_risk_score,
                       safety_reason, groundedness_score, error_message, created_at, updated_at
                FROM chat_turns
                WHERE id = ?
                """,
                (turn_id,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        return ChatTurn(
            id=row[0],
            session_id=row[1],
            query_text=row[2],
            answer_text=row[3],
            retrieved_chunks_json=row[4],
            context_used_json=row[5],
            status=row[6],
            safety_status=row[7],
            safety_risk_score=row[8],
            safety_reason=row[9],
            groundedness_score=row[10],
            error_message=row[11],
            created_at=row[12],
            updated_at=row[13],
        )

    @staticmethod
    def list_turns_by_session(session_id: str) -> List[ChatTurn]:
        """List all turns for a session."""
        with get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, session_id, query_text, answer_text, retrieved_chunks_json,
                       context_used_json, status, safety_status, safety_risk_score,
                       safety_reason, groundedness_score, error_message, created_at, updated_at
                FROM chat_turns
                WHERE session_id = ?
                ORDER BY created_at ASC
                """,
                (session_id,),
            )
            rows = cursor.fetchall()

        return [
            ChatTurn(
                id=row[0],
                session_id=row[1],
                query_text=row[2],
                answer_text=row[3],
                retrieved_chunks_json=row[4],
                context_used_json=row[5],
                status=row[6],
                safety_status=row[7],
                safety_risk_score=row[8],
                safety_reason=row[9],
                groundedness_score=row[10],
                error_message=row[11],
                created_at=row[12],
                updated_at=row[13],
            )
            for row in rows
        ]

    @staticmethod
    def update_turn_status(
        turn_id: str,
        status: str,
        answer_text: Optional[str] = None,
        safety_status: Optional[str] = None,
        safety_risk_score: Optional[float] = None,
        safety_reason: Optional[str] = None,
        groundedness_score: Optional[float] = None,
        error_message: Optional[str] = None,
    ) -> ChatTurn:
        """Update turn status and optionally answer/error/safety fields."""
        query = "UPDATE chat_turns SET status = ?, updated_at = CURRENT_TIMESTAMP"
        params = [status]

        if answer_text is not None:
            query += ", answer_text = ?"
            params.append(answer_text)
        
        if safety_status is not None:
            query += ", safety_status = ?"
            params.append(safety_status)

        if safety_risk_score is not None:
            query += ", safety_risk_score = ?"
            params.append(safety_risk_score)

        if safety_reason is not None:
            query += ", safety_reason = ?"
            params.append(safety_reason)

        if groundedness_score is not None:
            query += ", groundedness_score = ?"
            params.append(groundedness_score)

        if error_message is not None:
            query += ", error_message = ?"
            params.append(error_message)

        query += " WHERE id = ?"
        params.append(turn_id)

        with get_connection() as connection:
            connection.execute(query, params)

        return ChatRepository.get_turn(turn_id)

    @staticmethod
    def create_citation(
        id: str,
        turn_id: str,
        chunk_id: str,
        document_id: str,
        quote_text: Optional[str] = None,
        metadata_json: str = "{}",
    ) -> Citation:
        """Create a new citation."""
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO citations (id, turn_id, chunk_id, document_id, quote_text, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (id, turn_id, chunk_id, document_id, quote_text, metadata_json),
            )
        return ChatRepository.get_citation(id)

    @staticmethod
    def get_citation(citation_id: str) -> Optional[Citation]:
        """Get a citation by ID."""
        with get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, turn_id, chunk_id, document_id, quote_text, metadata_json, created_at
                FROM citations
                WHERE id = ?
                """,
                (citation_id,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        return Citation(
            id=row[0],
            turn_id=row[1],
            chunk_id=row[2],
            document_id=row[3],
            quote_text=row[4],
            metadata_json=row[5],
            created_at=row[6],
        )

    @staticmethod
    def list_citations_by_turn(turn_id: str) -> List[Citation]:
        """List all citations for a turn."""
        with get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, turn_id, chunk_id, document_id, quote_text, metadata_json, created_at
                FROM citations
                WHERE turn_id = ?
                ORDER BY created_at ASC
                """,
                (turn_id,),
            )
            rows = cursor.fetchall()

        return [
            Citation(
                id=row[0],
                turn_id=row[1],
                chunk_id=row[2],
                document_id=row[3],
                quote_text=row[4],
                metadata_json=row[5],
                created_at=row[6],
            )
            for row in rows
        ]
