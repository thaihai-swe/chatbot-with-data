from dataclasses import dataclass


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    collection_id: str | None
    source_type: str
    title: str | None
    source_url: str | None
    section_name: str | None
    page_number: int | None
    chunk_order: int
    chunk_text: str
    content_hash: str
    parent_chunk_id: str | None
    child_chunk_ids_json: str | None
    semantic_metadata_json: str | None
    created_at: str
