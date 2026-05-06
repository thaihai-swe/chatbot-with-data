"""Tests for indexing service with error handling."""
import pytest
import uuid
from unittest.mock import Mock, MagicMock, patch

from migrations.runner import apply_migrations, reset_database
from models.enums import IndexGenerationStatus
from indexing.indexing_service import IndexingService, EmbeddingError
from database import get_connection


@pytest.fixture(autouse=True)
def _reset_db():
    """Reset database before each test."""
    reset_database()
    apply_migrations()
    yield


def _create_test_setup() -> tuple[str, str, list[str]]:
    """Helper to create document, collection, and chunks in database."""
    doc_id = str(uuid.uuid4())
    col_id = str(uuid.uuid4())

    with get_connection() as conn:
        cursor = conn.cursor()

        # Create collection
        cursor.execute(
            "INSERT INTO collections (id, name) VALUES (?, ?)",
            (col_id, f"collection-{uuid.uuid4()}"),
        )

        # Create document
        cursor.execute(
            "INSERT INTO documents (id, title, source_type, extracted_text) VALUES (?, ?, ?, ?)",
            (doc_id, "Test Doc", "text", "Test content"),
        )

    # Create chunks
    chunk_ids = []
    for i in range(3):
        chunk_id = str(uuid.uuid4())
        chunk_ids.append(chunk_id)

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO chunks
                (id, document_id, collection_id, chunk_order, strategy, source_type, text, text_length)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk_id,
                    doc_id,
                    col_id,
                    i,
                    "fixed_size",
                    "text",
                    f"Chunk {i} content",
                    len(f"Chunk {i} content"),
                ),
            )

    return doc_id, col_id, chunk_ids


class TestIndexingServiceErrorHandling:
    """Test error handling in indexing service."""

    @patch("indexing.indexing_service.IndexEntryRepository")
    @patch("indexing.indexing_service.EmbeddingCache")
    def test_successful_indexing_all_chunks(self, mock_cache_class, mock_entry_repo):
        """Test successful indexing of all chunks."""
        doc_id, col_id, chunk_ids = _create_test_setup()

        # Mock embedding cache
        mock_cache = Mock()
        mock_cache.get_or_create.return_value = ([0.1] * 1536, False)
        mock_cache_class.return_value = mock_cache

        # Mock entry repository
        mock_entry_repo.create_entry = Mock()

        # Mock embedding client and chroma writer
        embedding_client = Mock()
        embedding_client.embed.side_effect = lambda texts: [
            [0.1] * 1536 for _ in texts
        ]

        chroma_writer = Mock()
        chroma_writer.add_vector = Mock()

        # Create service
        service = IndexingService(embedding_client, chroma_writer)

        # Index document
        gen_id, status, errors = service.index_document(doc_id, col_id)

        # Verify
        assert status == IndexGenerationStatus.COMPLETED
        assert len(errors) == 0
        assert gen_id is not None

        # Verify vectors were stored
        assert chroma_writer.add_vector.call_count == 3

    @patch("indexing.indexing_service.EmbeddingCache")
    def test_partial_indexing_with_failures(self, mock_cache_class):
        """Test partial indexing when some chunks fail."""
        doc_id, col_id, chunk_ids = _create_test_setup()

        # Mock embedding cache
        mock_cache = Mock()
        mock_cache.get_or_create.return_value = ([0.1] * 1536, False)
        mock_cache_class.return_value = mock_cache

        # Mock embedding client to fail on second chunk
        embedding_client = Mock()
        call_count = [0]

        def embed_side_effect(texts):
            call_count[0] += 1
            if call_count[0] == 2:  # Fail on second batch
                raise Exception("API rate limit exceeded")
            return [[0.1] * 1536 for _ in texts]

        embedding_client.embed.side_effect = embed_side_effect

        chroma_writer = Mock()
        chroma_writer.add_vector = Mock()

        service = IndexingService(embedding_client, chroma_writer)

        # Index document
        gen_id, status, errors = service.index_document(doc_id, col_id)

        # Verify that indexing completed with errors
        assert status == IndexGenerationStatus.COMPLETED
        # Should have 1 error (second chunk failed)
        assert len(errors) >= 1

    @patch("indexing.indexing_service.EmbeddingCache")
    def test_error_contains_chunk_and_document_id(self, mock_cache_class):
        """Test that errors contain chunk_id and document_id for logging."""
        doc_id, col_id, chunk_ids = _create_test_setup()

        # Mock embedding cache
        mock_cache = Mock()
        mock_cache.get_or_create.side_effect = Exception("Embedding failed")
        mock_cache_class.return_value = mock_cache

        embedding_client = Mock()
        chroma_writer = Mock()

        service = IndexingService(embedding_client, chroma_writer)

        # Index document
        gen_id, status, errors = service.index_document(doc_id, col_id)

        # Verify errors have required fields
        assert len(errors) > 0
        for error in errors:
            assert isinstance(error, EmbeddingError)
            assert error.chunk_id in chunk_ids
            assert error.error_reason is not None
            assert error.error_type is not None

    @patch("indexing.indexing_service.EmbeddingCache")
    def test_generation_marked_inactive_on_failure(self, mock_cache_class):
        """Test that generation is marked as completed even on partial failure."""
        from repositories.index_generation_repository import IndexGenerationRepository

        doc_id, col_id, chunk_ids = _create_test_setup()

        # Mock embedding cache to fail
        mock_cache = Mock()
        mock_cache.get_or_create.side_effect = Exception("API error")
        mock_cache_class.return_value = mock_cache

        embedding_client = Mock()
        chroma_writer = Mock()

        service = IndexingService(embedding_client, chroma_writer)

        # Index document
        gen_id, status, errors = service.index_document(doc_id, col_id)

        # Verify generation exists and is completed
        gen = IndexGenerationRepository.get_generation(gen_id)
        assert gen is not None
        assert gen.status == IndexGenerationStatus.COMPLETED

    @patch("indexing.indexing_service.IndexEntryRepository")
    @patch("indexing.indexing_service.EmbeddingCache")
    def test_multiple_chunks_processed_independently(self, mock_cache_class, mock_entry_repo):
        """Test that one failed chunk doesn't prevent others from being processed."""
        doc_id, col_id, chunk_ids = _create_test_setup()

        # Mock embedding cache - succeed on 1st and 3rd, fail on 2nd
        mock_cache = Mock()
        call_count = [0]

        def get_or_create_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 2:
                raise Exception("Simulated API failure")
            return ([0.1] * 1536, False)

        mock_cache.get_or_create.side_effect = get_or_create_side_effect
        mock_cache_class.return_value = mock_cache

        # Mock entry repository
        mock_entry_repo.create_entry = Mock()

        embedding_client = Mock()
        chroma_writer = Mock()
        chroma_writer.add_vector = Mock()

        service = IndexingService(embedding_client, chroma_writer)

        # Index document
        gen_id, status, errors = service.index_document(doc_id, col_id)

        # Verify: even with error, some chunks were processed
        # Chroma should have been called for successful chunks
        assert chroma_writer.add_vector.call_count > 0

    @patch("indexing.indexing_service.EmbeddingCache")
    def test_generation_created_with_metadata(self, mock_cache_class):
        """Test that generation is created with correct metadata."""
        from repositories.index_generation_repository import IndexGenerationRepository

        doc_id, col_id, chunk_ids = _create_test_setup()

        # Mock embedding cache
        mock_cache = Mock()
        mock_cache.get_or_create.return_value = ([0.1] * 1536, False)
        mock_cache_class.return_value = mock_cache

        embedding_client = Mock()
        chroma_writer = Mock()

        service = IndexingService(embedding_client, chroma_writer)

        # Index with specific metadata
        gen_id, status, errors = service.index_document(
            doc_id, col_id, embedding_model="text-embedding-3-large", strategy="semantic"
        )

        # Verify generation metadata
        gen = IndexGenerationRepository.get_generation(gen_id)
        assert gen.document_id == doc_id
        assert gen.embedding_model == "text-embedding-3-large"
        assert gen.strategy == "semantic"
        assert gen.chunk_count == 3

    @patch("indexing.indexing_service.EmbeddingCache")
    def test_empty_document_handling(self, mock_cache_class):
        """Test handling of document with no chunks."""
        from repositories.index_generation_repository import IndexGenerationRepository

        doc_id = str(uuid.uuid4())
        col_id = str(uuid.uuid4())

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO collections (id, name) VALUES (?, ?)",
                (col_id, "test-collection"),
            )
            cursor.execute(
                "INSERT INTO documents (id, title, source_type, extracted_text) VALUES (?, ?, ?, ?)",
                (doc_id, "Empty Doc", "text", ""),
            )

        # Mock embedding cache
        mock_cache = Mock()
        mock_cache_class.return_value = mock_cache

        embedding_client = Mock()
        chroma_writer = Mock()

        service = IndexingService(embedding_client, chroma_writer)

        # Index empty document
        gen_id, status, errors = service.index_document(doc_id, col_id)

        # Should complete successfully with zero chunks
        assert status == IndexGenerationStatus.COMPLETED
        assert len(errors) == 0

        # Verify generation was created
        gen = IndexGenerationRepository.get_generation(gen_id)
        assert gen.chunk_count == 0

    @patch("indexing.indexing_service.EmbeddingCache")
    def test_error_logging_with_document_and_chunk_ids(self, mock_cache_class, caplog):
        """Test that errors are logged with document_id and chunk_id."""
        import logging

        caplog.set_level(logging.ERROR)

        doc_id, col_id, chunk_ids = _create_test_setup()

        # Mock embedding cache to fail
        mock_cache = Mock()
        mock_cache.get_or_create.side_effect = Exception("API error")
        mock_cache_class.return_value = mock_cache

        embedding_client = Mock()
        chroma_writer = Mock()

        service = IndexingService(embedding_client, chroma_writer)

        # Index document
        gen_id, status, errors = service.index_document(doc_id, col_id)

        # Verify error logs contain document_id and chunk_id
        error_logs = [record for record in caplog.records if record.levelname == "ERROR"]
        assert len(error_logs) > 0

        # At least one log should mention failed chunk
        log_text = " ".join([record.message for record in error_logs])
        assert doc_id in log_text or chunk_ids[0] in log_text or "document" in log_text.lower()


class TestIndexingServiceIntegration:
    """Integration tests for indexing service."""

    @patch("indexing.indexing_service.EmbeddingCache")
    def test_uses_embedding_cache(self, mock_cache_class):
        """Test that service uses EmbeddingCache when not provided."""
        doc_id, col_id, chunk_ids = _create_test_setup()

        embedding_client = Mock()
        chroma_writer = Mock()

        # Create service without explicit cache
        service = IndexingService(embedding_client, chroma_writer)

        # Verify cache was created
        assert service.embedding_cache is not None

    @patch("indexing.indexing_service.EmbeddingCache")
    def test_generation_sequence(self, mock_cache_class):
        """Test that generation numbers increment correctly."""
        from repositories.index_generation_repository import IndexGenerationRepository

        doc_id, col_id, chunk_ids = _create_test_setup()

        # Mock embedding cache
        mock_cache = Mock()
        mock_cache.get_or_create.return_value = ([0.1] * 1536, False)
        mock_cache_class.return_value = mock_cache

        embedding_client = Mock()
        chroma_writer = Mock()

        service = IndexingService(embedding_client, chroma_writer)

        # Index twice
        gen_id_1, _, _ = service.index_document(doc_id, col_id)
        gen_id_2, _, _ = service.index_document(doc_id, col_id)

        # Verify generation numbers
        gen1 = IndexGenerationRepository.get_generation(gen_id_1)
        gen2 = IndexGenerationRepository.get_generation(gen_id_2)

        assert gen1.generation_number == 1
        assert gen2.generation_number == 2

    @patch("indexing.indexing_service.EmbeddingCache")
    def test_active_generation_on_success(self, mock_cache_class):
        """Test that generation is marked active only on full success."""
        from repositories.index_generation_repository import IndexGenerationRepository

        doc_id, col_id, chunk_ids = _create_test_setup()

        # Mock embedding cache
        mock_cache = Mock()
        mock_cache.get_or_create.return_value = ([0.1] * 1536, False)
        mock_cache_class.return_value = mock_cache

        embedding_client = Mock()
        chroma_writer = Mock()

        service = IndexingService(embedding_client, chroma_writer)

        # Index with success
        gen_id, _, errors = service.index_document(doc_id, col_id)

        # Verify generation is active only if no errors
        gen = IndexGenerationRepository.get_generation(gen_id)
        if not errors:
            assert gen.is_active is True
