from dataclasses import dataclass


@dataclass
class IndexRecord:
    collection_name: str
    document_id: str
    chunk_id: str
    embedding_model: str
