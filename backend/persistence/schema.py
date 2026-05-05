import sqlite3
from pathlib import Path


SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS collections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        collection_id TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        description TEXT,
        routing_description TEXT,
        is_default INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id TEXT NOT NULL UNIQUE,
        collection_id TEXT,
        source_type TEXT NOT NULL,
        source_path TEXT,
        source_url TEXT,
        source_identity TEXT,
        source_filename TEXT,
        title TEXT,
        raw_text TEXT,
        ingestion_status TEXT NOT NULL,
        duplicate_status TEXT,
        deletion_state TEXT NOT NULL DEFAULT 'active',
        file_hash TEXT,
        text_hash TEXT,
        freshness_metadata TEXT,
        created_at TEXT NOT NULL,
        last_indexed_at TEXT,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (collection_id) REFERENCES collections(collection_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ingestion_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id TEXT NOT NULL UNIQUE,
        document_id TEXT,
        source_type TEXT NOT NULL,
        source_identifier TEXT,
        status TEXT NOT NULL,
        duplicate_class TEXT,
        error_message TEXT,
        user_decision TEXT,
        payload_json TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (document_id) REFERENCES documents(document_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS duplicate_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id TEXT NOT NULL,
        matched_document_id TEXT,
        detection_method TEXT NOT NULL,
        duplicate_status TEXT NOT NULL,
        similarity_score REAL,
        decision TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (attempt_id) REFERENCES ingestion_attempts(attempt_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS chunk_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chunk_id TEXT NOT NULL UNIQUE,
        document_id TEXT NOT NULL,
        collection_id TEXT,
        source_type TEXT NOT NULL,
        title TEXT,
        source_url TEXT,
        section_name TEXT,
        page_number INTEGER,
        chunk_order INTEGER NOT NULL,
        chunk_text TEXT NOT NULL,
        content_hash TEXT,
        parent_chunk_id TEXT,
        child_chunk_ids_json TEXT,
        semantic_metadata_json TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (document_id) REFERENCES documents(document_id),
        FOREIGN KEY (collection_id) REFERENCES collections(collection_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_documents_document_id ON documents(document_id)",
    "CREATE INDEX IF NOT EXISTS idx_documents_collection_id ON documents(collection_id)",
    "CREATE INDEX IF NOT EXISTS idx_documents_source_type ON documents(source_type)",
    "CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(ingestion_status)",
    "CREATE INDEX IF NOT EXISTS idx_ingestion_attempts_document_id ON ingestion_attempts(document_id)",
    "CREATE INDEX IF NOT EXISTS idx_ingestion_attempts_status ON ingestion_attempts(status)",
    "CREATE INDEX IF NOT EXISTS idx_duplicate_logs_attempt_id ON duplicate_logs(attempt_id)",
    "CREATE INDEX IF NOT EXISTS idx_chunk_metadata_document_id ON chunk_metadata(document_id)",
    "CREATE INDEX IF NOT EXISTS idx_chunk_metadata_collection_id ON chunk_metadata(collection_id)",
    """
    CREATE TABLE IF NOT EXISTS chat_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL UNIQUE,
        user_id TEXT,
        selected_collection_id TEXT,
        retrieval_mode TEXT NOT NULL,
        metadata_json TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (selected_collection_id) REFERENCES collections(collection_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id TEXT NOT NULL UNIQUE,
        session_id TEXT NOT NULL,
        turn_id TEXT,
        turn_order INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        answer_status TEXT NOT NULL,
        refusal_category TEXT,
        retrieval_mode_used TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS turn_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        turn_id TEXT NOT NULL UNIQUE,
        session_id TEXT NOT NULL,
        user_message_id TEXT,
        assistant_message_id TEXT,
        question_text TEXT NOT NULL,
        selected_collection_id TEXT,
        retrieval_mode TEXT NOT NULL,
        terminal_status TEXT NOT NULL,
        result_type TEXT,
        answerability_score REAL,
        completion_timestamp TEXT,
        cancel_requested INTEGER NOT NULL DEFAULT 0,
        is_streaming INTEGER NOT NULL DEFAULT 0,
        retrieval_metadata_json TEXT,
        generation_metadata_json TEXT,
        supporting_metrics_json TEXT,
        packed_context_json TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id),
        FOREIGN KEY (selected_collection_id) REFERENCES collections(collection_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS refusal_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        refusal_id TEXT NOT NULL UNIQUE,
        turn_id TEXT NOT NULL,
        reason_category TEXT NOT NULL,
        refusal_text TEXT NOT NULL,
        supporting_metrics_json TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (turn_id) REFERENCES turn_metadata(turn_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS citation_references (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        citation_id TEXT NOT NULL UNIQUE,
        turn_id TEXT NOT NULL,
        chunk_id TEXT NOT NULL,
        document_id TEXT NOT NULL,
        document_title TEXT,
        page_or_section TEXT,
        source_url TEXT,
        content_snippet TEXT NOT NULL,
        retrieval_score REAL,
        retrieval_mode TEXT NOT NULL,
        embedding_or_rerank_score REAL,
        inline_text_reference TEXT,
        citation_order INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (turn_id) REFERENCES turn_metadata(turn_id),
        FOREIGN KEY (document_id) REFERENCES documents(document_id),
        FOREIGN KEY (chunk_id) REFERENCES chunk_metadata(chunk_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS chat_turn_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        log_id TEXT NOT NULL UNIQUE,
        turn_id TEXT NOT NULL,
        session_id TEXT NOT NULL,
        question_text TEXT NOT NULL,
        retrieval_mode_used TEXT NOT NULL,
        retrieved_chunk_count INTEGER NOT NULL,
        answerability_score REAL,
        refusal_category TEXT,
        answer_length_tokens INTEGER NOT NULL DEFAULT 0,
        final_citation_count INTEGER NOT NULL DEFAULT 0,
        metadata_json TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (turn_id) REFERENCES turn_metadata(turn_id),
        FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS run_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL UNIQUE,
        turn_id TEXT NOT NULL UNIQUE,
        session_id TEXT NOT NULL,
        query_text TEXT NOT NULL,
        answer_text TEXT,
        refusal_reason TEXT,
        answerability_flag INTEGER NOT NULL DEFAULT 0,
        answerability_score REAL,
        groundedness_status TEXT NOT NULL,
        prompt_injection_result TEXT NOT NULL,
        prompt_injection_risk_score REAL NOT NULL DEFAULT 0,
        safety_issue_count INTEGER NOT NULL DEFAULT 0,
        latency_ms INTEGER NOT NULL DEFAULT 0,
        token_count INTEGER NOT NULL DEFAULT 0,
        model_name TEXT,
        embedding_model TEXT,
        retrieval_mode_used TEXT,
        selected_collection_id TEXT,
        result_type TEXT NOT NULL,
        warning_summary TEXT,
        excluded_evidence_notice TEXT,
        retrieval_metadata_json TEXT,
        generation_metadata_json TEXT,
        answerability_json TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (turn_id) REFERENCES turn_metadata(turn_id),
        FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id),
        FOREIGN KEY (selected_collection_id) REFERENCES collections(collection_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS safety_issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        issue_id TEXT NOT NULL UNIQUE,
        run_id TEXT NOT NULL,
        issue_scope TEXT NOT NULL,
        detection_method TEXT NOT NULL,
        risk_score REAL NOT NULL,
        matched_pattern TEXT,
        classifier_reason TEXT,
        affected_document_id TEXT,
        affected_chunk_id TEXT,
        recommended_action TEXT NOT NULL,
        final_action TEXT NOT NULL,
        final_decision TEXT,
        content_snippet TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (run_id) REFERENCES run_records(run_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS debug_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL UNIQUE,
        snapshot_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (run_id) REFERENCES run_records(run_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS observability_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metadata_id TEXT NOT NULL UNIQUE,
        run_id TEXT NOT NULL,
        metadata_key TEXT NOT NULL,
        metadata_value_json TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (run_id) REFERENCES run_records(run_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_chat_messages_turn_id ON chat_messages(turn_id)",
    "CREATE INDEX IF NOT EXISTS idx_turn_metadata_session_id ON turn_metadata(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_turn_metadata_status ON turn_metadata(terminal_status)",
    "CREATE INDEX IF NOT EXISTS idx_refusal_logs_turn_id ON refusal_logs(turn_id)",
    "CREATE INDEX IF NOT EXISTS idx_citation_references_turn_id ON citation_references(turn_id)",
    "CREATE INDEX IF NOT EXISTS idx_chat_turn_logs_session_id ON chat_turn_logs(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_run_records_session_id ON run_records(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_run_records_turn_id ON run_records(turn_id)",
    "CREATE INDEX IF NOT EXISTS idx_safety_issues_run_id ON safety_issues(run_id)",
    "CREATE INDEX IF NOT EXISTS idx_observability_metadata_run_id ON observability_metadata(run_id)",
)

MIGRATION_COLUMNS = {
    "collections": (
        ("routing_description", "TEXT"),
    ),
    "documents": (
        ("source_identity", "TEXT"),
        ("source_filename", "TEXT"),
        ("raw_text", "TEXT"),
        ("file_hash", "TEXT"),
        ("text_hash", "TEXT"),
        ("freshness_metadata", "TEXT"),
        ("updated_at", "TEXT"),
    ),
    "ingestion_attempts": (
        ("duplicate_class", "TEXT"),
        ("payload_json", "TEXT"),
    ),
    "duplicate_logs": (
        ("decision", "TEXT"),
    ),
    "chunk_metadata": (
        ("chunk_text", "TEXT"),
        ("parent_chunk_id", "TEXT"),
        ("child_chunk_ids_json", "TEXT"),
        ("semantic_metadata_json", "TEXT"),
    ),
    "chat_sessions": (
        ("user_id", "TEXT"),
        ("metadata_json", "TEXT"),
    ),
    "chat_messages": (
        ("turn_id", "TEXT"),
        ("refusal_category", "TEXT"),
        ("retrieval_mode_used", "TEXT"),
    ),
    "turn_metadata": (
        ("cancel_requested", "INTEGER NOT NULL DEFAULT 0"),
        ("is_streaming", "INTEGER NOT NULL DEFAULT 0"),
        ("packed_context_json", "TEXT"),
    ),
    "citation_references": (
        ("embedding_or_rerank_score", "REAL"),
        ("inline_text_reference", "TEXT"),
    ),
    "chat_turn_logs": (
        ("metadata_json", "TEXT"),
    ),
    "run_records": (
        ("warning_summary", "TEXT"),
        ("excluded_evidence_notice", "TEXT"),
        ("retrieval_metadata_json", "TEXT"),
        ("generation_metadata_json", "TEXT"),
        ("answerability_json", "TEXT"),
    ),
    "safety_issues": (
        ("final_decision", "TEXT"),
        ("content_snippet", "TEXT"),
    ),
}


def _table_columns(connection, table_name):
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row[1] for row in rows}


def _apply_migrations(connection):
    for table_name, columns in MIGRATION_COLUMNS.items():
        existing_columns = _table_columns(connection, table_name)
        for column_name, column_type in columns:
            if column_name in existing_columns:
                continue
            try:
                connection.execute(
                    f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                )
            except sqlite3.OperationalError as exc:
                if "duplicate column name" not in str(exc).lower():
                    raise


def init_schema(sqlite_path):
    sqlite_path = Path(sqlite_path)
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(sqlite_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)
        _apply_migrations(connection)
        connection.commit()
