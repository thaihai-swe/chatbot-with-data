from dataclasses import dataclass


@dataclass
class Document:
    document_id: str
    collection_id: str | None
    source_type: str
    source_path: str | None
    source_url: str | None
    source_identity: str | None
    source_filename: str | None
    title: str | None
    raw_text: str | None
    ingestion_status: str
    duplicate_status: str | None
    deletion_state: str
    file_hash: str | None
    text_hash: str | None
    freshness_metadata: str | None
    created_at: str
    last_indexed_at: str | None
    updated_at: str
