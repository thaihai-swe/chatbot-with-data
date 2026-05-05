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
]


DROP_STATEMENTS = [
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


def reset_database() -> None:
    with get_connection() as connection:
        for statement in DROP_STATEMENTS:
            connection.execute(statement)
