# Plan: Split Chat and Embedding Configuration

## Execution Order
1. Update `backend/config.py` to add `embedding_api_base` and `embedding_api_key` to the `Settings` class, with fallback logic.
2. Identify all service files that use `openai_api_base` or `openai_api_key` for embedding generation.
3. Refactor those services to use the new embedding-specific settings if provided.
4. Verify functionality via manual testing (e.g., pointing `EMBEDDING_API_BASE` to a non-existent URL should fail embedding-only tasks while chat remains functional).

## Impacted Boundaries
- `backend/config.py`: Configuration loading.
- `backend/embeddings/`: Service logic that performs embedding generation.
- Potentially `backend/ingestion/` if it calls embedding services directly.

## Proving Strategy
- Unit tests: Mock `Settings` to return both shared and separate configs, verifying the correct values are returned for embedding and chat.
- Integration tests: Run a test that generates embeddings with `EMBEDDING_API_BASE` set to a dummy URL, confirming it attempts to reach that URL.

## Rollback Posture
- Configuration changes are simple: revert `backend/config.py` and environment variables.
- Re-run tests to ensure stability.
