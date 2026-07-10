from __future__ import annotations

from database import get_connection


SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version TEXT PRIMARY KEY,
        applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS collections (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        is_default INTEGER NOT NULL DEFAULT 0,
        routing_enabled INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        deleted_at TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        source_type TEXT NOT NULL,
        source_uri TEXT,
        canonical_source_uri TEXT,
        filename TEXT,
        mime_type TEXT,
        file_hash TEXT,
        normalized_text_hash TEXT,
        extracted_text TEXT,
        metadata_json TEXT NOT NULL DEFAULT '{}',
        version_of_document_id TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        deleted_at TEXT,
        FOREIGN KEY(version_of_document_id) REFERENCES documents(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS document_collections (
        document_id TEXT NOT NULL,
        collection_id TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (document_id, collection_id),
        FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE,
        FOREIGN KEY(collection_id) REFERENCES collections(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ingestion_attempts (
        id TEXT PRIMARY KEY,
        document_id TEXT,
        source_type TEXT NOT NULL,
        status TEXT NOT NULL,
        submitted_filename TEXT,
        source_uri TEXT,
        canonical_source_uri TEXT,
        mime_type TEXT,
        artifact_path TEXT,
        snapshot_path TEXT,
        title TEXT,
        extracted_text TEXT,
        metadata_json TEXT NOT NULL DEFAULT '{}',
        file_hash TEXT,
        normalized_text_hash TEXT,
        duplicate_status TEXT,
        duplicate_match_document_id TEXT,
        duplicate_evidence_json TEXT,
        error_message TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        completed_at TEXT,
        FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE SET NULL,
        FOREIGN KEY(duplicate_match_document_id) REFERENCES documents(id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ingestion_attempt_collections (
        ingestion_attempt_id TEXT NOT NULL,
        collection_id TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (ingestion_attempt_id, collection_id),
        FOREIGN KEY(ingestion_attempt_id) REFERENCES ingestion_attempts(id) ON DELETE CASCADE,
        FOREIGN KEY(collection_id) REFERENCES collections(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS lifecycle_events (
        id TEXT PRIMARY KEY,
        document_id TEXT,
        ingestion_attempt_id TEXT,
        event_type TEXT NOT NULL,
        from_status TEXT,
        to_status TEXT,
        details_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE,
        FOREIGN KEY(ingestion_attempt_id) REFERENCES ingestion_attempts(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS duplicate_decisions (
        id TEXT PRIMARY KEY,
        ingestion_attempt_id TEXT NOT NULL,
        document_id TEXT,
        matched_document_id TEXT,
        classification TEXT NOT NULL,
        detection_method TEXT NOT NULL,
        evidence_json TEXT NOT NULL DEFAULT '{}',
        action TEXT NOT NULL,
        final_status TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(ingestion_attempt_id) REFERENCES ingestion_attempts(id) ON DELETE CASCADE,
        FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE SET NULL,
        FOREIGN KEY(matched_document_id) REFERENCES documents(id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS chunks (
        id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        collection_id TEXT NOT NULL,
        chunk_order INTEGER NOT NULL,
        strategy TEXT NOT NULL,
        source_type TEXT NOT NULL,
        title TEXT,
        section_title TEXT,
        page_number INTEGER,
        source_url TEXT,
        text TEXT NOT NULL,
        text_length INTEGER NOT NULL,
        parent_chunk_id TEXT,
        fallback_applied INTEGER NOT NULL DEFAULT 0,
        semantic_score REAL,
        metadata_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE,
        FOREIGN KEY(collection_id) REFERENCES collections(id) ON DELETE CASCADE,
        FOREIGN KEY(parent_chunk_id) REFERENCES chunks(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_chunks_collection_id ON chunks(collection_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_chunks_parent_id ON chunks(parent_chunk_id)
    """,
    """
    CREATE TABLE IF NOT EXISTS embeddings (
        id TEXT PRIMARY KEY,
        chunk_id TEXT NOT NULL,
        embedding_model TEXT NOT NULL,
        embedding_model_version TEXT,
        embedding_vector BLOB NOT NULL,
        input_text_hash TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(chunk_id) REFERENCES chunks(id) ON DELETE CASCADE,
        UNIQUE(chunk_id, embedding_model)
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id ON embeddings(chunk_id)
    """,
    """
    CREATE TABLE IF NOT EXISTS index_generations (
        id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        generation_number INTEGER NOT NULL,
        status TEXT NOT NULL,
        strategy TEXT NOT NULL,
        settings_hash TEXT,
        embedding_model TEXT,
        chunk_count INTEGER,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        completed_at TEXT,
        FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE,
        UNIQUE(document_id, generation_number)
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_index_generations_document_id ON index_generations(document_id)
    """,
    """
    CREATE TABLE IF NOT EXISTS index_entries (
        id TEXT PRIMARY KEY,
        chunk_id TEXT NOT NULL,
        embedding_id TEXT NOT NULL,
        document_id TEXT NOT NULL,
        collection_id TEXT NOT NULL,
        generation_id TEXT NOT NULL,
        vector_db_id TEXT,
        is_active INTEGER NOT NULL DEFAULT 1,
        chunk_order INTEGER NOT NULL,
        parent_chunk_id TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(chunk_id) REFERENCES chunks(id) ON DELETE CASCADE,
        FOREIGN KEY(embedding_id) REFERENCES embeddings(id) ON DELETE CASCADE,
        FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE,
        FOREIGN KEY(collection_id) REFERENCES collections(id) ON DELETE CASCADE,
        FOREIGN KEY(generation_id) REFERENCES index_generations(id) ON DELETE CASCADE,
        FOREIGN KEY(parent_chunk_id) REFERENCES chunks(id) ON DELETE SET NULL
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_index_entries_chunk_id ON index_entries(chunk_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_index_entries_document_id ON index_entries(document_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_index_entries_collection_id ON index_entries(collection_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_index_entries_generation_id ON index_entries(generation_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_index_entries_is_active ON index_entries(is_active)
    """,
    """
    CREATE TABLE IF NOT EXISTS chat_sessions (
        id TEXT PRIMARY KEY,
        collection_id TEXT,
        metadata_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(collection_id) REFERENCES collections(id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS chat_turns (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        query_text TEXT NOT NULL,
        answer_text TEXT,
        retrieved_chunks_json TEXT NOT NULL DEFAULT '[]',
        context_used_json TEXT NOT NULL DEFAULT '{}',
        status TEXT NOT NULL DEFAULT 'pending',
        safety_status TEXT,
        safety_risk_score REAL,
        safety_reason TEXT,
        groundedness_score REAL,
        error_message TEXT,
        provenance_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_chat_turns_session_id ON chat_turns(session_id)
    """,
    """
    CREATE TABLE IF NOT EXISTS citations (
        id TEXT PRIMARY KEY,
        turn_id TEXT NOT NULL,
        chunk_id TEXT NOT NULL,
        document_id TEXT NOT NULL,
        quote_text TEXT,
        metadata_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(turn_id) REFERENCES chat_turns(id) ON DELETE CASCADE,
        FOREIGN KEY(chunk_id) REFERENCES chunks(id) ON DELETE CASCADE,
        FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_citations_turn_id ON citations(turn_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_chat_sessions_collection_id ON chat_sessions(collection_id)
    """,
    """
    CREATE TABLE IF NOT EXISTS chunk_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chunk_id TEXT NOT NULL UNIQUE,
        note_text TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(chunk_id) REFERENCES chunks(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_chunk_notes_chunk_id ON chunk_notes(chunk_id)
    """,
    """
    CREATE TABLE IF NOT EXISTS evaluation_runs (
        id TEXT PRIMARY KEY,
        dataset_name TEXT,
        model_name TEXT,
        total_cases INTEGER,
        passed_cases INTEGER,
        overall_recall REAL,
        overall_groundedness REAL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_evaluation_runs_created_at ON evaluation_runs(created_at)
    """,
]


DROP_STATEMENTS = [
    "DROP TABLE IF EXISTS evaluation_runs",
    "DROP TABLE IF EXISTS chunk_notes",
    "DROP TABLE IF EXISTS citations",
    "DROP TABLE IF EXISTS chat_turns",
    "DROP TABLE IF EXISTS chat_sessions",
    "DROP TABLE IF EXISTS index_entries",
    "DROP TABLE IF EXISTS index_generations",
    "DROP TABLE IF EXISTS embeddings",
    "DROP TABLE IF EXISTS chunks",
    "DROP TABLE IF EXISTS duplicate_decisions",
    "DROP TABLE IF EXISTS lifecycle_events",
    "DROP TABLE IF EXISTS ingestion_attempt_collections",
    "DROP TABLE IF EXISTS ingestion_attempts",
    "DROP TABLE IF EXISTS document_collections",
    "DROP TABLE IF EXISTS documents",
    "DROP TABLE IF EXISTS collections",
    "DROP TABLE IF EXISTS schema_migrations",
]


def apply_migrations() -> None:
    with get_connection() as connection:
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)
        connection.execute(
            "INSERT OR IGNORE INTO schema_migrations(version) VALUES (?)",
            ("0001_initial",),
        )
        connection.execute(
            "INSERT OR IGNORE INTO schema_migrations(version) VALUES (?)",
            ("0002_chunking_and_indexing",),
        )

        # 0003_safety_and_groundedness
        cursor = connection.execute("SELECT 1 FROM schema_migrations WHERE version = ?", ("0003_safety_and_groundedness",))
        if not cursor.fetchone():
            try:
                # connection.execute("ALTER TABLE chat_turns ADD COLUMN safety_status TEXT")
                # connection.execute("ALTER TABLE chat_turns ADD COLUMN safety_risk_score REAL")
                # connection.execute("ALTER TABLE chat_turns ADD COLUMN safety_reason TEXT")
                # connection.execute("ALTER TABLE chat_turns ADD COLUMN groundedness_score REAL")
                connection.execute(
                    "INSERT INTO schema_migrations(version) VALUES (?)",
                    ("0003_safety_and_groundedness",),
                )
            except Exception as e:
                # If columns already exist (e.g. from a fresh CREATE TABLE), just record the migration
                if "duplicate column name" in str(e).lower():
                    connection.execute(
                        "INSERT OR IGNORE INTO schema_migrations(version) VALUES (?)",
                        ("0003_safety_and_groundedness",),
                    )
                else:
                    raise e

        # 0004_multi_collection_chat
        cursor = connection.execute("SELECT 1 FROM schema_migrations WHERE version = ?", ("0004_multi_collection_chat",))
        if not cursor.fetchone():
            # Check if chat_session_collections exists in the database
            table_check = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='chat_session_collections'"
            )
            if table_check.fetchone():
                # Data migration: Move existing collection_id to the mapping table
                connection.execute(
                    """
                    INSERT INTO chat_session_collections (session_id, collection_id)
                    SELECT id, collection_id FROM chat_sessions WHERE collection_id IS NOT NULL
                    """
                )
            connection.execute(
                "INSERT INTO schema_migrations(version) VALUES (?)",
                ("0004_multi_collection_chat",),
            )

        # 0005_user_annotations
        cursor = connection.execute("SELECT 1 FROM schema_migrations WHERE version = ?", ("0005_user_annotations",))
        if not cursor.fetchone():
            # chunk_notes table created via SCHEMA_STATEMENTS; just record the version
            connection.execute(
                "INSERT INTO schema_migrations(version) VALUES (?)",
                ("0005_user_annotations",),
            )

        # 0006_single_collection_chat
        cursor = connection.execute("SELECT 1 FROM schema_migrations WHERE version = ?", ("0006_single_collection_chat",))
        if not cursor.fetchone():
            # Check if old table exists
            table_check = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='chat_session_collections'"
            )
            if table_check.fetchone():
                connection.execute(
                    """
                    UPDATE chat_sessions
                    SET collection_id = (
                        SELECT collection_id
                        FROM chat_session_collections
                        WHERE chat_session_collections.session_id = chat_sessions.id
                        LIMIT 1
                    )
                    WHERE EXISTS (
                        SELECT 1
                        FROM chat_session_collections
                        WHERE chat_session_collections.session_id = chat_sessions.id
                    )
                    """
                )
                connection.execute("DROP TABLE IF EXISTS chat_session_collections")

            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_chat_sessions_collection_id ON chat_sessions(collection_id)"
            )
            connection.execute(
                "INSERT INTO schema_migrations(version) VALUES (?)",
                ("0006_single_collection_chat",),
            )

        # 0007_provenance_json
        cursor = connection.execute(
            "SELECT 1 FROM schema_migrations WHERE version = ?",
            ("0007_provenance_json",),
        )
        if not cursor.fetchone():
            try:
                connection.execute(
                    "ALTER TABLE chat_turns ADD COLUMN provenance_json TEXT NOT NULL DEFAULT '{}'"
                )
            except Exception as e:
                # Fresh CREATE TABLE already has the column
                if "duplicate column name" not in str(e).lower():
                    raise e
            connection.execute(
                "INSERT INTO schema_migrations(version) VALUES (?)",
                ("0007_provenance_json",),
            )

        # 0008_ablation_variants
        cursor = connection.execute(
            "SELECT 1 FROM schema_migrations WHERE version = ?",
            ("0008_ablation_variants",),
        )
        if not cursor.fetchone():
            try:
                connection.execute(
                    "ALTER TABLE evaluation_runs ADD COLUMN config_variant_name TEXT"
                )
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    raise e
            try:
                connection.execute(
                    "ALTER TABLE evaluation_runs ADD COLUMN config_snapshot_json TEXT"
                )
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    raise e
            connection.execute(
                "INSERT INTO schema_migrations(version) VALUES (?)",
                ("0008_ablation_variants",),
            )


def reset_database() -> None:
    with get_connection() as connection:
        for statement in DROP_STATEMENTS:
            connection.execute(statement)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        print("Resetting database...")
        reset_database()
        print("Database reset.")

    print("Applying migrations...")
    apply_migrations()
    print("Migrations applied successfully.")
