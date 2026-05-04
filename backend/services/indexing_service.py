import hashlib
import json

from backend.utils import utcnow_iso


class IndexingService:
    def __init__(self, chroma_client, collection_prefix="collection", embedding_model="local-hash-v1", dimensions=32):
        self.chroma_client = chroma_client
        self.collection_prefix = collection_prefix
        self.embedding_model = embedding_model
        self.dimensions = dimensions

    def _collection_name(self, collection_id):
        suffix = collection_id or "unassigned"
        return f"{self.collection_prefix}_{suffix}"

    def _embed(self, text):
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = []
        for index in range(self.dimensions):
            values.append(digest[index % len(digest)] / 255.0)
        return values

    def index_chunks(self, document, chunks):
        collection = self.chroma_client.get_or_create_collection(
            name=self._collection_name(document.get("collection_id"))
        )
        ids = [chunk["chunk_id"] for chunk in chunks]
        embeddings = [self._embed(chunk["chunk_text"]) for chunk in chunks]
        metadatas = []
        documents = []

        for chunk in chunks:
            metadata = {
                "document_id": chunk["document_id"],
                "collection_id": chunk.get("collection_id") or "",
                "source_type": chunk["source_type"],
                "title": chunk.get("title") or "",
                "source_url": chunk.get("source_url") or "",
                "section_name": chunk.get("section_name") or "",
                "page_number": chunk.get("page_number") or 0,
                "chunk_order": chunk["chunk_order"],
                "content_hash": chunk["content_hash"],
            }
            metadatas.append(metadata)
            documents.append(chunk["chunk_text"])

        existing = collection.get(ids=ids)
        if existing and existing.get("ids"):
            collection.delete(ids=ids)

        collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)
        return {
            "collection_name": collection.name,
            "document_id": document["document_id"],
            "chunk_count": len(chunks),
            "embedding_model": self.embedding_model,
            "indexed_at": utcnow_iso(),
        }

    def delete_document(self, document):
        collection = self.chroma_client.get_or_create_collection(
            name=self._collection_name(document.get("collection_id"))
        )
        existing = collection.get(where={"document_id": document["document_id"]})
        if existing.get("ids"):
            collection.delete(ids=existing["ids"])

    def move_document(self, document, chunks, new_collection_id):
        self.delete_document(document)
        moved_document = dict(document)
        moved_document["collection_id"] = new_collection_id
        moved_chunks = []
        for chunk in chunks:
            moved_chunk = dict(chunk)
            moved_chunk["collection_id"] = new_collection_id
            moved_chunks.append(moved_chunk)
        return self.index_chunks(moved_document, moved_chunks)
