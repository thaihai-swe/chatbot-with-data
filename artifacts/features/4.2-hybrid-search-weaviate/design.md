# Technical Design: Feature 4.2 - Hybrid Search with Weaviate Migration

## 1. Abstraction Layer (SOLID)
We will introduce an Abstract Base Class (ABC) `VectorStore` to decouple the application from ChromaDB.

### Interface: `backend/indexing/base.py`
```python
class VectorStore(ABC):
    @abstractmethod
    def add_vectors(self, vectors: list[tuple[str, list[float], dict]]) -> int:
        pass

    @abstractmethod
    def query_hybrid(
        self, 
        query_text: str, 
        query_embedding: list[float], 
        alpha: float, 
        k: int, 
        collection_ids: Optional[list[str]] = None
    ) -> list[tuple[str, float, dict]]:
        pass

    @abstractmethod
    def delete_by_document(self, document_id: str) -> int:
        pass

    @abstractmethod
    def delete_by_collection(self, collection_id: str) -> int:
        pass
```

## 2. Weaviate Implementation
### Schema Definition
We will define a `DocumentChunk` class in Weaviate with the following properties:
- `text`: text (indexed for BM25)
- `chunk_id`: text (uuid)
- `document_id`: text (uuid, filterable)
- `collection_id`: text (uuid, filterable)
- `chunk_order`: int
- `metadata`: text (JSON string for flexibility)

### Hybrid Search Logic
Weaviate v4 `hybrid` search will be used:
```python
result = (
    client.collections.get("DocumentChunk")
    .query.hybrid(
        query=query_text,
        vector=query_embedding,
        alpha=alpha,
        limit=k,
        filters=filter_logic # based on collection_ids
    )
)
```

## 3. Dependency Injection
A `get_vector_store` dependency will be used to provide the `WeaviateVectorStore` instance. Since Chroma is being removed, the factory will be simplified to directly instantiate the Weaviate provider.

## 4. Migration Strategy
1. **Clean Break:** The `ChromaVectorWriter` and all Chroma-specific configuration will be deleted.
2. **Re-indexing:** The system will start with an empty Weaviate instance. Users must re-index their documents.
3. **Interface Adoption:** `IndexingService` and `RetrievalService` will be refactored to depend on the `VectorStore` ABC, ensuring that future provider swaps (e.g., Pinecone) remain trivial even if Chroma is gone.

## 5. Infrastructure
A new `docker-compose.yml` (or update to existing) will include:
- `weaviate`: semitechnologies/weaviate:1.27.0
- `env`: `QUERY_DEFAULTS_LIMIT: 25`, `AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'`
