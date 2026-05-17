# Implementation Plan: Feature 4.2 - Hybrid Search with Weaviate Migration

## 1. Execution Order
1. **Infrastructure:** Add Weaviate to `docker-compose.yml` and ensure connectivity.
2. **Abstraction:** Define `VectorStore` ABC.
3. **Deconstruction:** Remove `ChromaVectorWriter` and delete `.chroma_db` reference logic.
4. **Implementation:** Create `WeaviateVectorStore`.
5. **Integration:** Update `RetrievalService` and `IndexingService` to use the new `VectorStore` implementation.
6. **Configuration:** Update `RetrievalSettings` and backend config.
7. **Validation:** End-to-end testing of Keyword, Semantic, and Hybrid modes.

## 2. Impacted Boundaries
- `backend/indexing/`: Major changes (Removal of Chroma, new Weaviate implementation).
- `backend/chat/retrieval.py`: Refactor to use the new interface and support hybrid parameters.
- `backend/config.py`: Remove Chroma settings, add Weaviate settings.
- `backend/schemas/settings.py`: Align with Weaviate-specific parameters if needed.

## 3. Proving Strategy
- **Unit Tests:** Verify `VectorStore` interface compliance.
- **Integration Tests:** Use a temporary Weaviate container (or local dev instance) to verify BM25 vs. Vector vs. Hybrid results.
- **Manual Verification:** Use the Document Library to re-index a document and verify it appears in Weaviate queries.

## 4. Rollback Posture
- This is a non-reversible migration at the code level (destructive to Chroma support). Rollback would require a git revert of the deletion tasks.
- No data migration is attempted; users must re-index.
