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
        collection_id: Optional[str] = None,
        metadata_json: str = "{}",
    ) -> ChatSession:
        """Create a new chat session."""
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO chat_sessions (id, collection_id, metadata_json)
                VALUES (?, ?, ?)
                """,
                (id, collection_id, metadata_json),
            )
        return ChatRepository.get_session(id)

    @staticmethod
    def get_session(session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID."""
        with get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, collection_id, created_at, updated_at, metadata_json
                FROM chat_sessions
                WHERE id = ?
                """,
                (session_id,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        return ChatSession(
            id=row[0],
            collection_id=row[1],
            created_at=row[2],
            updated_at=row[3],
            metadata_json=row[4],
        )

    @staticmethod
    def list_sessions() -> List[ChatSession]:
        """List all chat sessions."""
        with get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, collection_id, created_at, updated_at, metadata_json
                FROM chat_sessions
                ORDER BY created_at DESC
                """
            )
            rows = cursor.fetchall()

        return [
            ChatSession(
                id=row[0],
                collection_id=row[1],
                created_at=row[2],
                updated_at=row[3],
                metadata_json=row[4],
            )
            for row in rows
        ]

    @staticmethod
    def create_turn(
        id: str,
        session_id: str,
        query_text: str,
        answer_text: Optional[str] = None,
        retrieved_chunks_json: str = "[]",
        context_used_json: str = "{}",
        status: str = "pending",
        error_message: Optional[str] = None,
    ) -> ChatTurn:
        """Create a new chat turn."""
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO chat_turns
                (id, session_id, query_text, answer_text, retrieved_chunks_json,
                 context_used_json, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    id,
                    session_id,
                    query_text,
                    answer_text,
                    retrieved_chunks_json,
                    context_used_json,
                    status,
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
                       context_used_json, status, error_message, created_at, updated_at
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
            error_message=row[7],
            created_at=row[8],
            updated_at=row[9],
        )

    @staticmethod
    def list_turns_by_session(session_id: str) -> List[ChatTurn]:
        """List all turns for a session."""
        with get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT id, session_id, query_text, answer_text, retrieved_chunks_json,
                       context_used_json, status, error_message, created_at, updated_at
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
                error_message=row[7],
                created_at=row[8],
                updated_at=row[9],
            )
            for row in rows
        ]

    @staticmethod
    def update_turn_status(
        turn_id: str,
        status: str,
        answer_text: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> ChatTurn:
        """Update turn status and optionally answer/error."""
        query = "UPDATE chat_turns SET status = ?, updated_at = CURRENT_TIMESTAMP"
        params = [status]

        if answer_text is not None:
            query += ", answer_text = ?"
            params.append(answer_text)
        
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
