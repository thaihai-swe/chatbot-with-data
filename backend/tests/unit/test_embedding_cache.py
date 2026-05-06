import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
import hashlib
from unittest.mock import Mock
import uuid

from database import get_connection
from migrations.runner import apply_migrations, reset_database
from repositories.embedding_repository import EmbeddingRepository, EmbeddingCache


@pytest.fixture(scope="function")
def setup_db():
    """Set up fresh database for each test."""
    reset_database()
    apply_migrations()
    yield
    reset_database()


def _create_test_chunk(text: str = "Test chunk content") -> str:
    """Helper to create a test chunk in the database."""
    doc_id = str(uuid.uuid4())
    collection_id = str(uuid.uuid4())
    chunk_id = str(uuid.uuid4())

    with get_connection() as conn:
        cursor = conn.cursor()

        # Create collection
        cursor.execute(
            """
            INSERT INTO collections (id, name)
            VALUES (?, ?)
            """,
            (collection_id, f"collection-{uuid.uuid4()}"),
        )

        # Create document
        cursor.execute(
            """
            INSERT INTO documents (id, title, source_type, extracted_text)
            VALUES (?, ?, ?, ?)
            """,
            (doc_id, "Test Doc", "text", ""),
        )

        # Create chunk
        cursor.execute(
            """
            INSERT INTO chunks
            (id, document_id, collection_id, chunk_order, strategy, source_type, text, text_length)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (chunk_id, doc_id, collection_id, 0, "fixed_size", "text", text, len(text)),
        )
        conn.commit()

    return chunk_id


@pytest.fixture
def sample_chunk_id(setup_db):
    """Sample chunk ID for testing (creates actual chunk in DB)."""
    return _create_test_chunk()


@pytest.fixture
def sample_vector():
    """Sample embedding vector (1536 dims like text-embedding-3-small)."""
    return [0.1] * 1536


@pytest.fixture
def sample_text():
    """Sample text for embedding."""
    return "This is a test chunk of text for embedding."


@pytest.fixture
def sample_text_hash(sample_text):
    """Compute hash of sample text."""
    return EmbeddingRepository.compute_text_hash(sample_text)


class TestEmbeddingRepository:
    """Test embedding repository CRUD operations."""

    def test_create_embedding(self, setup_db, sample_chunk_id, sample_vector, sample_text_hash):
        """Test creating an embedding."""
        embedding = EmbeddingRepository.create_embedding(
            chunk_id=sample_chunk_id,
            embedding_model="text-embedding-3-small",
            embedding_vector=sample_vector,
            input_text_hash=sample_text_hash,
        )

        assert embedding.id is not None
        assert embedding.chunk_id == sample_chunk_id
        assert embedding.embedding_model == "text-embedding-3-small"
        assert embedding.embedding_vector == sample_vector
        assert embedding.input_text_hash == sample_text_hash

    def test_create_embedding_with_version(self, setup_db, sample_chunk_id, sample_vector, sample_text_hash):
        """Test creating embedding with model version."""
        embedding = EmbeddingRepository.create_embedding(
            chunk_id=sample_chunk_id,
            embedding_model="text-embedding-3-small",
            embedding_vector=sample_vector,
            input_text_hash=sample_text_hash,
            embedding_model_version="20240519",
        )

        assert embedding.embedding_model_version == "20240519"

    def test_create_embedding_invalid_inputs(self, setup_db):
        """Test that creating embedding with invalid inputs raises error."""
        with pytest.raises(ValueError):
            EmbeddingRepository.create_embedding(
                chunk_id="",
                embedding_model="text-embedding-3-small",
                embedding_vector=[0.1] * 1536,
                input_text_hash="hash123",
            )

        with pytest.raises(ValueError):
            EmbeddingRepository.create_embedding(
                chunk_id="chunk-001",
                embedding_model="",
                embedding_vector=[0.1] * 1536,
                input_text_hash="hash123",
            )

    def test_get_cached_embedding_hit(self, setup_db, sample_chunk_id, sample_vector, sample_text_hash):
        """Test retrieving embedding from cache (cache hit)."""
        # Create an embedding
        EmbeddingRepository.create_embedding(
            chunk_id=sample_chunk_id,
            embedding_model="text-embedding-3-small",
            embedding_vector=sample_vector,
            input_text_hash=sample_text_hash,
        )

        # Retrieve it
        cached = EmbeddingRepository.get_cached_embedding(
            chunk_id=sample_chunk_id,
            embedding_model="text-embedding-3-small",
        )

        assert cached is not None
        assert cached.chunk_id == sample_chunk_id
        assert cached.embedding_vector == sample_vector

    def test_get_cached_embedding_miss(self, setup_db, sample_chunk_id):
        """Test retrieving embedding that doesn't exist (cache miss)."""
        cached = EmbeddingRepository.get_cached_embedding(
            chunk_id=sample_chunk_id,
            embedding_model="text-embedding-3-small",
        )

        assert cached is None

    def test_get_cached_embedding_different_model(self, setup_db, sample_chunk_id, sample_vector, sample_text_hash):
        """Test that different models have separate caches."""
        # Create embedding with one model
        EmbeddingRepository.create_embedding(
            chunk_id=sample_chunk_id,
            embedding_model="text-embedding-3-small",
            embedding_vector=sample_vector,
            input_text_hash=sample_text_hash,
        )

        # Try to retrieve with different model - should be cache miss
        cached = EmbeddingRepository.get_cached_embedding(
            chunk_id=sample_chunk_id,
            embedding_model="text-embedding-3-large",
        )

        assert cached is None

    def test_get_embedding_by_id(self, setup_db, sample_chunk_id, sample_vector, sample_text_hash):
        """Test retrieving embedding by ID."""
        created = EmbeddingRepository.create_embedding(
            chunk_id=sample_chunk_id,
            embedding_model="text-embedding-3-small",
            embedding_vector=sample_vector,
            input_text_hash=sample_text_hash,
        )

        # Retrieve by ID
        retrieved = EmbeddingRepository.get_embedding_by_id(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.chunk_id == sample_chunk_id

    def test_list_embeddings_by_chunk(self, setup_db, sample_chunk_id, sample_vector, sample_text_hash):
        """Test listing all embeddings for a chunk."""
        # Create multiple embeddings for same chunk with different models
        EmbeddingRepository.create_embedding(
            chunk_id=sample_chunk_id,
            embedding_model="text-embedding-3-small",
            embedding_vector=sample_vector,
            input_text_hash=sample_text_hash,
        )

        EmbeddingRepository.create_embedding(
            chunk_id=sample_chunk_id,
            embedding_model="text-embedding-3-large",
            embedding_vector=sample_vector,
            input_text_hash=sample_text_hash,
        )

        embeddings = EmbeddingRepository.list_embeddings_by_chunk(sample_chunk_id)

        assert len(embeddings) == 2
        models = {e.embedding_model for e in embeddings}
        assert models == {"text-embedding-3-small", "text-embedding-3-large"}

    def test_delete_embedding(self, setup_db, sample_chunk_id, sample_vector, sample_text_hash):
        """Test deleting an embedding."""
        created = EmbeddingRepository.create_embedding(
            chunk_id=sample_chunk_id,
            embedding_model="text-embedding-3-small",
            embedding_vector=sample_vector,
            input_text_hash=sample_text_hash,
        )

        deleted = EmbeddingRepository.delete_embedding(created.id)
        assert deleted is True

        # Verify it's gone
        retrieved = EmbeddingRepository.get_embedding_by_id(created.id)
        assert retrieved is None

    def test_delete_embeddings_by_chunk(self, setup_db, sample_chunk_id, sample_vector, sample_text_hash):
        """Test deleting all embeddings for a chunk."""
        # Create multiple embeddings
        EmbeddingRepository.create_embedding(
            chunk_id=sample_chunk_id,
            embedding_model="text-embedding-3-small",
            embedding_vector=sample_vector,
            input_text_hash=sample_text_hash,
        )

        EmbeddingRepository.create_embedding(
            chunk_id=sample_chunk_id,
            embedding_model="text-embedding-3-large",
            embedding_vector=sample_vector,
            input_text_hash=sample_text_hash,
        )

        # Delete all for chunk
        count = EmbeddingRepository.delete_embeddings_by_chunk(sample_chunk_id)
        assert count == 2

        # Verify all are gone
        embeddings = EmbeddingRepository.list_embeddings_by_chunk(sample_chunk_id)
        assert len(embeddings) == 0

    def test_compute_text_hash(self):
        """Test text hash computation."""
        text = "This is test text"
        hash1 = EmbeddingRepository.compute_text_hash(text)
        hash2 = EmbeddingRepository.compute_text_hash(text)

        # Same text produces same hash
        assert hash1 == hash2

        # Different text produces different hash
        hash3 = EmbeddingRepository.compute_text_hash("Different text")
        assert hash1 != hash3

        # Hash is SHA256 format (64 hex characters)
        assert len(hash1) == 64
        assert all(c in "0123456789abcdef" for c in hash1)

    def test_cache_is_valid(self, setup_db, sample_chunk_id, sample_vector, sample_text_hash):
        """Test cache validity checking."""
        embedding = EmbeddingRepository.create_embedding(
            chunk_id=sample_chunk_id,
            embedding_model="text-embedding-3-small",
            embedding_vector=sample_vector,
            input_text_hash=sample_text_hash,
        )

        # Same hash - cache is valid
        assert EmbeddingRepository.cache_is_valid(embedding, sample_text_hash) is True

        # Different hash - cache is invalid (text changed)
        different_hash = EmbeddingRepository.compute_text_hash("Different text")
        assert EmbeddingRepository.cache_is_valid(embedding, different_hash) is False


class TestEmbeddingCache:
    """Test high-level embedding cache interface."""

    def test_cache_hit(self, setup_db, sample_chunk_id, sample_text, sample_vector):
        """Test cache hit - no API call needed."""
        cache = EmbeddingCache(embedding_model="text-embedding-3-small")

        # First call - cache miss, calls create_fn
        create_fn = Mock(return_value=sample_vector)
        vector1, was_cached1 = cache.get_or_create(
            chunk_id=sample_chunk_id,
            text=sample_text,
            create_fn=create_fn,
        )

        assert vector1 == sample_vector
        assert was_cached1 is False
        assert create_fn.call_count == 1

        # Second call - cache hit, doesn't call create_fn
        vector2, was_cached2 = cache.get_or_create(
            chunk_id=sample_chunk_id,
            text=sample_text,
            create_fn=create_fn,
        )

        assert vector2 == sample_vector
        assert was_cached2 is True
        assert create_fn.call_count == 1  # Not called again

    def test_cache_miss_on_text_change(self, setup_db, sample_chunk_id, sample_text, sample_vector):
        """Test cache miss when text changes (text hash differs)."""
        cache = EmbeddingCache(embedding_model="text-embedding-3-small")

        create_fn = Mock(return_value=sample_vector)

        # First embedding
        vector1, was_cached1 = cache.get_or_create(
            chunk_id=sample_chunk_id,
            text=sample_text,
            create_fn=create_fn,
        )
        assert was_cached1 is False

        # Text changed - different hash triggers cache miss
        different_text = "This is completely different text now."
        different_vector = [0.2] * 1536

        create_fn.return_value = different_vector
        vector2, was_cached2 = cache.get_or_create(
            chunk_id=sample_chunk_id,
            text=different_text,
            create_fn=create_fn,
        )

        assert vector2 == different_vector
        assert was_cached2 is False
        assert create_fn.call_count == 2  # Called again for new text

    def test_different_models_separate_cache(self, setup_db, sample_chunk_id, sample_text, sample_vector):
        """Test that different embedding models have separate caches."""
        # Create embedding with small model
        cache_small = EmbeddingCache(embedding_model="text-embedding-3-small")
        create_fn_small = Mock(return_value=sample_vector)

        vector1, cached1 = cache_small.get_or_create(
            chunk_id=sample_chunk_id,
            text=sample_text,
            create_fn=create_fn_small,
        )
        assert cached1 is False

        # Create embedding with large model - should cache miss
        cache_large = EmbeddingCache(embedding_model="text-embedding-3-large")
        large_vector = [0.3] * 1536
        create_fn_large = Mock(return_value=large_vector)

        vector2, cached2 = cache_large.get_or_create(
            chunk_id=sample_chunk_id,
            text=sample_text,
            create_fn=create_fn_large,
        )
        assert cached2 is False

        # Both create functions were called (cache miss for each model)
        assert create_fn_small.call_count == 1
        assert create_fn_large.call_count == 1

    def test_get_cache_stats(self, setup_db, sample_chunk_id, sample_text, sample_vector):
        """Test retrieving cache statistics."""
        cache = EmbeddingCache(embedding_model="text-embedding-3-small")
        create_fn = Mock(return_value=sample_vector)

        # Create embeddings
        cache.get_or_create(
            chunk_id=sample_chunk_id,
            text=sample_text,
            create_fn=create_fn,
        )

        # Create another for large model
        cache_large = EmbeddingCache(embedding_model="text-embedding-3-large")
        cache_large.get_or_create(
            chunk_id=sample_chunk_id,
            text=sample_text,
            create_fn=Mock(return_value=sample_vector),
        )

        # Get stats
        stats = cache.get_cache_stats(sample_chunk_id)

        assert stats["chunk_id"] == sample_chunk_id
        assert stats["embedding_count"] == 2
        assert "text-embedding-3-small" in stats["models"]
        assert "text-embedding-3-large" in stats["models"]
        assert len(stats["embeddings"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
