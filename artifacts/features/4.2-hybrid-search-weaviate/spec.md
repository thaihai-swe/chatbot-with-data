# Specification: Feature 4.2 - Hybrid Search with Weaviate Migration

## 1. Problem Statement
The current RAG system is limited to semantic-only retrieval via ChromaDB, causing failures on queries requiring exact matches (e.g., product IDs, acronyms). Additionally, the codebase is tightly coupled to the `ChromaVectorWriter`, violating the Dependency Inversion Principle and hindering the adoption of more advanced hybrid search engines like Weaviate.

## 2. Outcomes & User Scenarios
- **Outcome:** The system provides significantly more accurate answers for keyword-heavy queries while maintaining a flexible, provider-agnostic architecture.
- **Scenario 1 (Hybrid Retrieval):** A user asks about "Part ID XYZ-123". The system uses Weaviate's hybrid search to find the exact chunk containing that ID, even if semantic similarity is low.
- **Scenario 2 (Provider Swapping):** A developer can implement a new `PineconeVectorStore` by implementing the `VectorStore` interface without modifying the `RetrievalService`.

## 3. Scope
- **In Scope:**
    - `VectorStore` Abstract Base Class (ABC) defining the core contract.
    - `WeaviateVectorStore` implementation using the Weaviate v4 Python client.
    - Full removal of ChromaDB-related code and storage logic.
    - Hybrid search integration in `RetrievalService` with configurable `alpha` (weight).
    - Local development setup via `docker-compose.yml`.
- **Out Of Scope:**
    - Support for multiple concurrent vector databases.
    - Migration scripts for Chroma data (re-indexing is required).
    - Advanced Weaviate features like "Generative Search".

## 4. Requirements

### REQ-001: VectorStore Abstraction
- The system MUST define an abstract base class `VectorStore` in `backend/indexing/base.py`.
- This interface will serve as the primary contract for all vector operations, ensuring the system is provider-agnostic for future iterations.

### REQ-002: Weaviate Implementation (Primary Store)
- `WeaviateVectorStore` MUST be the sole implementation of the `VectorStore` interface.
- ChromaDB code MUST be removed from the repository.

### REQ-003: Search Modes and Weight Integration
- `RetrievalService` MUST support three distinct search modes:
    - **Keyword Mode:** Retrieves results using BM25 scoring only.
    - **Semantic Mode:** Retrieves results using Vector similarity only.
    - **Hybrid Mode:** Retrieves results using a weighted combination of BM25 and Vector similarity.
- In **Hybrid Mode**, the system MUST allow configuration of the `alpha` (weight) parameter (0.0 to 1.0):
    - `alpha = 0.0` corresponds to Keyword Mode.
    - `alpha = 1.0` corresponds to Semantic Mode.
    - `0.0 < alpha < 1.0` provides a weighted hybrid result.
- The `search_mode` and `hybrid_weight` (alpha) MUST be sourced from `RetrievalSettings`.
- `RetrievalService` MUST be refactored to depend on `VectorStore` (injected).

### REQ-004: Configuration and Deployment
- `backend/config.py` MUST support a `VECTOR_STORE_PROVIDER` setting (defaulting to "weaviate").
- A `docker-compose.yml` MUST be provided to spin up a local Weaviate instance.

## 5. Acceptance Criteria
- **AC-001:** A unit test verifies that `WeaviateVectorStore` correctly implements the `VectorStore` interface.
- **AC-002:** An integration test confirms that a query for a unique keyword (e.g., "ID-999-B") returns the correct chunk when `alpha` is set to 0.5, even if the keyword has no semantic neighbor.
- **AC-003:** Deleting a document from the Document Library successfully removes all corresponding vectors from Weaviate.
- **AC-004:** The system starts successfully with a local Weaviate instance and logs "Connected to Weaviate".

## 6. Constraints & Assumptions
- **Assumption:** The user has Docker installed and can run the provided `docker-compose.yml`.
- **Constraint:** Re-indexing is mandatory. The system will not attempt to read from the old `.chroma_db` folder once switched.

## 7. Open Questions
- Should we provide a one-click "Clear All and Re-index" button in the UI to simplify the migration for users? (Recommended: Yes).
