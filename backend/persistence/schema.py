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
