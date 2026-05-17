# Proposal: Feature 4.2 - Hybrid Search with Weaviate Migration

## 1. Problem Statement
The current RAG pipeline relies exclusively on semantic (vector) search via ChromaDB. While effective for context, it fails on exact keyword matches (technical terms, acronyms, product IDs). Furthermore, the system is tightly coupled to ChromaDB, violating SOLID principles and making it difficult to switch providers (e.g., Pinecone, Weaviate, Elasticsearch) without significant refactoring.

## 2. Proposed Solution
We will replace ChromaDB with **Weaviate** to leverage its native hybrid search (BM25 + Vector) and unified retrieval API. To ensure future flexibility, we will introduce a `VectorStore` abstraction layer that decouples the application logic from the underlying database implementation.

## 3. Scope
- **In Scope:**
    - Implementation of a generic `VectorStore` interface (SOLID/Dependency Inversion).
    - New `WeaviateVectorStore` implementation of the interface.
    - Support for three explicit search modes: **Keyword**, **Semantic**, and **Hybrid**.
    - Configurable weights for keyword vs. semantic search in Hybrid mode.
    - Integration of Weaviate native hybrid search into the retrieval pipeline.
    - Support for local Weaviate deployment via Docker.
    - Automated re-indexing of existing collections (no raw data migration).
- **Out Of Scope:**
    - Migration of existing raw vector data from Chroma (re-indexing only).
    - Support for other vector databases (e.g., Pinecone) in this specific PR.
    - Multi-tenant Weaviate cloud configuration.

## 4. Architectural Changes
- **Interface:** Define `backend/indexing/base.py:VectorStore` with `add_vectors`, `query_hybrid`, `delete_by_document`, etc.
- **Factory:** Introduce a `VectorStoreFactory` to resolve the active implementation based on configuration.
- **Service Update:** Refactor `RetrievalService` and `IndexingService` to depend on the `VectorStore` interface rather than `ChromaVectorWriter`.

## 5. User Impact
- **Improved Retrieval:** Users will experience better accuracy for queries involving specific keywords.
- **System Stability:** The abstraction layer allows developers to swap the database in the future with minimal code changes.
- **Clean Slate:** Existing indexed data will need to be re-indexed via the Document Library.

## 6. Open Questions
- Should we use Weaviate's auto-schema generation or define explicit class properties?
- Do we want to expose Weaviate's `alpha` parameter (weight between keyword and vector) in the UI?
