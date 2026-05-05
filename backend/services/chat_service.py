import json

from backend.models.chat_message import ChatMessage
from backend.models.chat_session import ChatSession
from backend.persistence.db import get_connection
from backend.services.run_record_service import RunRecordService
from backend.utils import generate_id, json_dumps, utcnow_iso


class ChatSessionService:
    def __init__(self, sqlite_path):
        self.sqlite_path = sqlite_path

    def create_session(self, collection_id=None, retrieval_mode="semantic", user_id=None, metadata=None):
        now = utcnow_iso()
        session_id = generate_id("chat")
        with get_connection(self.sqlite_path) as connection:
            connection.execute(
                """
                INSERT INTO chat_sessions (
                    session_id, user_id, selected_collection_id, retrieval_mode,
                    metadata_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    user_id,
                    collection_id,
                    retrieval_mode,
                    json_dumps(metadata or {}),
                    now,
                    now,
                ),
            )
        return self.get_session(session_id)

    def list_sessions(self):
        with get_connection(self.sqlite_path) as connection:
            rows = connection.execute(
                """
                SELECT
                    s.*,
                    c.name AS collection_name,
                    (
                        SELECT content
                        FROM chat_messages m
                        WHERE m.session_id = s.session_id
                        ORDER BY m.turn_order DESC, m.created_at DESC
                        LIMIT 1
                    ) AS last_message
                FROM chat_sessions s
                LEFT JOIN collections c ON c.collection_id = s.selected_collection_id
                ORDER BY s.updated_at DESC
                """
            ).fetchall()
        return [self._session_payload(row) for row in rows]

    def get_session(self, session_id):
        with get_connection(self.sqlite_path) as connection:
            row = connection.execute(
                """
                SELECT s.*, c.name AS collection_name
                FROM chat_sessions s
                LEFT JOIN collections c ON c.collection_id = s.selected_collection_id
                WHERE s.session_id = ?
                """,
                (session_id,),
            ).fetchone()
        if not row:
            return None
        payload = self._session_payload(row)
        payload["turns"] = self.get_session_history(session_id)
        return payload

    def _session_payload(self, row):
        payload = ChatSession.from_row(row).to_dict()
        payload["collection_name"] = row.get("collection_name")
        payload["metadata"] = json.loads(row.get("metadata_json") or "{}")
        if "last_message" in row:
            payload["last_message"] = row.get("last_message")
        return payload

    def _next_turn_order(self, session_id):
        with get_connection(self.sqlite_path) as connection:
            row = connection.execute(
                "SELECT COALESCE(MAX(turn_order), 0) AS max_turn_order FROM chat_messages WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        return (row or {}).get("max_turn_order", 0) + 1

    def create_turn(self, session_id, question_text, selected_collection_id=None, retrieval_mode="semantic", is_streaming=False):
        turn_id = generate_id("turn")
        message_id = generate_id("msg")
        now = utcnow_iso()
        turn_order = self._next_turn_order(session_id)
        with get_connection(self.sqlite_path) as connection:
            connection.execute(
                """
                INSERT INTO chat_messages (
                    message_id, session_id, turn_id, turn_order, role, content,
                    answer_status, refusal_category, retrieval_mode_used, created_at, updated_at
                ) VALUES (?, ?, ?, ?, 'user', ?, 'pending', NULL, ?, ?, ?)
                """,
                (
                    message_id,
                    session_id,
                    turn_id,
                    turn_order,
                    question_text,
                    retrieval_mode,
                    now,
                    now,
                ),
            )
            connection.execute(
                """
                INSERT INTO turn_metadata (
                    turn_id, session_id, user_message_id, assistant_message_id,
                    question_text, selected_collection_id, retrieval_mode, terminal_status,
                    result_type, answerability_score, completion_timestamp, cancel_requested,
                    is_streaming, retrieval_metadata_json, generation_metadata_json,
                    supporting_metrics_json, packed_context_json, created_at, updated_at
                ) VALUES (?, ?, ?, NULL, ?, ?, ?, 'pending', NULL, NULL, NULL, 0, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    turn_id,
                    session_id,
                    message_id,
                    question_text,
                    selected_collection_id,
                    retrieval_mode,
                    1 if is_streaming else 0,
                    json_dumps({}),
                    json_dumps({}),
                    json_dumps({}),
                    json_dumps([]),
                    now,
                    now,
                ),
            )
            connection.execute(
                "UPDATE chat_sessions SET updated_at = ? WHERE session_id = ?",
                (now, session_id),
            )
        return self.get_turn(turn_id)

    def complete_turn(
        self,
        turn_id,
        result_type,
        assistant_content,
        terminal_status,
        refusal_category=None,
        retrieval_mode_used=None,
        answerability_score=None,
        retrieval_metadata=None,
        generation_metadata=None,
        supporting_metrics=None,
        packed_context=None,
        citations=None,
    ):
        turn = self.get_turn(turn_id)
        if not turn:
            return None

        message_id = generate_id("msg")
        now = utcnow_iso()
        assistant_order = self._next_turn_order(turn["session_id"])
        with get_connection(self.sqlite_path) as connection:
            connection.execute(
                """
                INSERT INTO chat_messages (
                    message_id, session_id, turn_id, turn_order, role, content,
                    answer_status, refusal_category, retrieval_mode_used, created_at, updated_at
                ) VALUES (?, ?, ?, ?, 'assistant', ?, ?, ?, ?, ?, ?)
                """,
                (
                    message_id,
                    turn["session_id"],
                    turn_id,
                    assistant_order,
                    assistant_content,
                    terminal_status,
                    refusal_category,
                    retrieval_mode_used or turn["retrieval_mode"],
                    now,
                    now,
                ),
            )
            connection.execute(
                """
                UPDATE turn_metadata
                SET assistant_message_id = ?, terminal_status = ?, result_type = ?,
                    answerability_score = ?, completion_timestamp = ?, retrieval_metadata_json = ?,
                    generation_metadata_json = ?, supporting_metrics_json = ?, packed_context_json = ?,
                    updated_at = ?
                WHERE turn_id = ?
                """,
                (
                    message_id,
                    terminal_status,
                    result_type,
                    answerability_score,
                    now,
                    json_dumps(retrieval_metadata or {}),
                    json_dumps(generation_metadata or {}),
                    json_dumps(supporting_metrics or {}),
                    json_dumps(packed_context or []),
                    now,
                    turn_id,
                ),
            )
            if refusal_category:
                connection.execute(
                    """
                    INSERT INTO refusal_logs (
                        refusal_id, turn_id, reason_category, refusal_text,
                        supporting_metrics_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        generate_id("refusal"),
                        turn_id,
                        refusal_category,
                        assistant_content,
                        json_dumps(supporting_metrics or {}),
                        now,
                    ),
                )
            connection.execute("DELETE FROM citation_references WHERE turn_id = ?", (turn_id,))
            for order, citation in enumerate(citations or [], start=1):
                connection.execute(
                    """
                    INSERT INTO citation_references (
                        citation_id, turn_id, chunk_id, document_id, document_title,
                        page_or_section, source_url, content_snippet, retrieval_score,
                        retrieval_mode, embedding_or_rerank_score, inline_text_reference,
                        citation_order, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        citation["citation_id"],
                        turn_id,
                        citation["chunk_id"],
                        citation["document_id"],
                        citation.get("document_title"),
                        citation.get("page_or_section"),
                        citation.get("source_url"),
                        citation["content_snippet"],
                        citation.get("retrieval_score"),
                        citation["retrieval_mode"],
                        citation.get("embedding_or_rerank_score"),
                        citation.get("inline_text_reference"),
                        order,
                        now,
                    ),
                )
            connection.execute(
                "UPDATE chat_sessions SET updated_at = ? WHERE session_id = ?",
                (now, turn["session_id"]),
            )
        return self.get_turn(turn_id)

    def mark_turn_cancel_requested(self, turn_id):
        now = utcnow_iso()
        with get_connection(self.sqlite_path) as connection:
            connection.execute(
                """
                UPDATE turn_metadata
                SET cancel_requested = 1, updated_at = ?
                WHERE turn_id = ?
                """,
                (now, turn_id),
            )
        return self.get_turn(turn_id)

    def mark_turn_cancelled(self, turn_id, retrieval_metadata=None, supporting_metrics=None):
        turn = self.get_turn(turn_id)
        if not turn:
            return None
        return self.complete_turn(
            turn_id=turn_id,
            result_type="cancelled",
            assistant_content="Generation cancelled.",
            terminal_status="cancelled",
            retrieval_mode_used=turn["retrieval_mode"],
            retrieval_metadata=retrieval_metadata,
            generation_metadata={},
            supporting_metrics=supporting_metrics,
            packed_context=[],
            citations=[],
        )

    def get_turn(self, turn_id):
        with get_connection(self.sqlite_path) as connection:
            row = connection.execute(
                "SELECT * FROM turn_metadata WHERE turn_id = ?",
                (turn_id,),
            ).fetchone()
        return row

    def get_session_history(self, session_id):
        with get_connection(self.sqlite_path) as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM chat_messages
                WHERE session_id = ?
                ORDER BY turn_order ASC, created_at ASC
                """,
                (session_id,),
            ).fetchall()
        return [ChatMessage.from_row(row).to_dict() for row in rows]

    def get_recent_session_history(self, session_id, limit=6):
        with get_connection(self.sqlite_path) as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM (
                    SELECT *
                    FROM chat_messages
                    WHERE session_id = ?
                    ORDER BY turn_order DESC, created_at DESC
                    LIMIT ?
                ) recent_messages
                ORDER BY turn_order ASC, created_at ASC
                """,
                (session_id, limit),
            ).fetchall()
        return [ChatMessage.from_row(row).to_dict() for row in rows]

    def get_turn_messages(self, turn_id):
        with get_connection(self.sqlite_path) as connection:
            rows = connection.execute(
                "SELECT * FROM chat_messages WHERE turn_id = ? ORDER BY turn_order ASC, created_at ASC",
                (turn_id,),
            ).fetchall()
        return [ChatMessage.from_row(row).to_dict() for row in rows]

    def get_citations_for_turn(self, turn_id):
        with get_connection(self.sqlite_path) as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM citation_references
                WHERE turn_id = ?
                ORDER BY citation_order ASC
                """,
                (turn_id,),
            ).fetchall()
        return rows

    def get_citation_detail(self, session_id, citation_id):
        with get_connection(self.sqlite_path) as connection:
            row = connection.execute(
                """
                SELECT
                    cr.*,
                    cm.chunk_order,
                    cm.chunk_text AS full_snippet,
                    cm.page_number,
                    cm.section_name
                FROM citation_references cr
                JOIN turn_metadata tm ON tm.turn_id = cr.turn_id
                LEFT JOIN chunk_metadata cm ON cm.chunk_id = cr.chunk_id
                WHERE tm.session_id = ? AND cr.citation_id = ?
                """,
                (session_id, citation_id),
            ).fetchone()
        if not row:
            return None
        payload = dict(row)
        payload["retrieval_mode"] = row["retrieval_mode"]
        payload["page_or_section"] = row.get("page_or_section") or (
            f"page {row['page_number']}" if row.get("page_number") else row.get("section_name")
        )
        return payload

    def log_turn(
        self,
        turn_id,
        session_id,
        question_text,
        retrieval_mode_used,
        retrieved_chunk_count,
        answerability_score,
        refusal_category,
        answer_length_tokens,
        final_citation_count,
        metadata=None,
    ):
        with get_connection(self.sqlite_path) as connection:
            connection.execute(
                """
                INSERT INTO chat_turn_logs (
                    log_id, turn_id, session_id, question_text, retrieval_mode_used,
                    retrieved_chunk_count, answerability_score, refusal_category,
                    answer_length_tokens, final_citation_count, metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    generate_id("chatlog"),
                    turn_id,
                    session_id,
                    question_text,
                    retrieval_mode_used,
                    retrieved_chunk_count,
                    answerability_score,
                    refusal_category,
                    answer_length_tokens,
                    final_citation_count,
                    json_dumps(metadata or {}),
                    utcnow_iso(),
                ),
            )

    def list_logs(self, session_id=None):
        sql = "SELECT * FROM chat_turn_logs"
        params = []
        if session_id:
            sql += " WHERE session_id = ?"
            params.append(session_id)
        sql += " ORDER BY created_at DESC"
        with get_connection(self.sqlite_path) as connection:
            rows = connection.execute(sql, params).fetchall()
        return rows

    def record_run(self, **kwargs):
        return RunRecordService(self.sqlite_path).create_run_record(**kwargs)

    def get_run_by_turn(self, turn_id):
        return RunRecordService(self.sqlite_path).get_run_by_turn(turn_id)

    def list_runs_for_session(self, session_id):
        return RunRecordService(self.sqlite_path).list_runs_for_session(session_id)
