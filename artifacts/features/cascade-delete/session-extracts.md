<!-- triaged: true, date: 2026-07-12 -->

# Session Extracts: cascade-delete

## Extracted Candidates

- [PROMOTED] EXT-001: Python pytest Mocking gotcha for module-level imports
  - Category: Heuristic
  - Trigger: Patching WeaviateVectorStore or class-level imports in Python tests where the target class is already imported at the module level in other modules.
  - Working heuristic: When patching a class (e.g. `WeaviateVectorStore`), if it is imported at the module level (e.g., `from indexing.weaviate_store import WeaviateVectorStore` in `ingestion.service`), mocking the class at its definition module (`indexing.weaviate_store.WeaviateVectorStore`) will not retroactively update references in the already-imported modules. We must patch the reference inside the target module where it is used (e.g., `ingestion.service.WeaviateVectorStore`).
  - Evidence: Refused connection error to Weaviate (localhost:8080) when running the full test suite in `pytest`, because `ingestion.service` was pre-imported by other test files before the patch was applied, binding it to the unmocked class.
