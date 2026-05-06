"""Unit tests for IndexGeneration and IndexEntry models."""
import pytest
from models.enums import IndexGenerationStatus
from models.index_generation import IndexGeneration
from models.index_entry import IndexEntry


class TestIndexGeneration:
    """Test IndexGeneration dataclass."""

    def test_create_index_generation(self):
        """Test creating a valid IndexGeneration."""
        gen = IndexGeneration(
            id="gen-001",
            document_id="doc-001",
            generation_number=1,
            status=IndexGenerationStatus.COMPLETED,
            strategy="fixed_size",
            chunk_count=10,
            is_active=True,
        )
        assert gen.id == "gen-001"
        assert gen.document_id == "doc-001"
        assert gen.generation_number == 1
        assert gen.status == IndexGenerationStatus.COMPLETED
        assert gen.strategy == "fixed_size"
        assert gen.chunk_count == 10
        assert gen.is_active is True

    def test_create_with_string_status(self):
        """Test that string status is converted to enum."""
        gen = IndexGeneration(
            id="gen-001",
            document_id="doc-001",
            generation_number=1,
            status="completed",
            strategy="fixed_size",
            chunk_count=10,
            is_active=True,
        )
        assert gen.status == IndexGenerationStatus.COMPLETED
        assert isinstance(gen.status, IndexGenerationStatus)

    def test_create_with_optional_fields(self):
        """Test creating with optional fields."""
        gen = IndexGeneration(
            id="gen-001",
            document_id="doc-001",
            generation_number=1,
            status=IndexGenerationStatus.COMPLETED,
            strategy="fixed_size",
            chunk_count=5,
            is_active=True,
            settings_hash="abc123",
            embedding_model="text-embedding-3-small",
            created_at="2026-05-05T10:00:00",
            completed_at="2026-05-05T10:05:00",
        )
        assert gen.settings_hash == "abc123"
        assert gen.embedding_model == "text-embedding-3-small"
        assert gen.created_at == "2026-05-05T10:00:00"
        assert gen.completed_at == "2026-05-05T10:05:00"

    def test_invalid_empty_id(self):
        """Test that empty id raises ValueError."""
        with pytest.raises(ValueError, match="id is required"):
            IndexGeneration(
                id="",
                document_id="doc-001",
                generation_number=1,
                status=IndexGenerationStatus.COMPLETED,
                strategy="fixed_size",
                chunk_count=10,
                is_active=True,
            )

    def test_invalid_empty_document_id(self):
        """Test that empty document_id raises ValueError."""
        with pytest.raises(ValueError, match="document_id is required"):
            IndexGeneration(
                id="gen-001",
                document_id="",
                generation_number=1,
                status=IndexGenerationStatus.COMPLETED,
                strategy="fixed_size",
                chunk_count=10,
                is_active=True,
            )

    def test_invalid_negative_generation_number(self):
        """Test that negative generation_number raises ValueError."""
        with pytest.raises(ValueError, match="generation_number must be >= 0"):
            IndexGeneration(
                id="gen-001",
                document_id="doc-001",
                generation_number=-1,
                status=IndexGenerationStatus.COMPLETED,
                strategy="fixed_size",
                chunk_count=10,
                is_active=True,
            )

    def test_invalid_empty_strategy(self):
        """Test that empty strategy raises ValueError."""
        with pytest.raises(ValueError, match="strategy is required"):
            IndexGeneration(
                id="gen-001",
                document_id="doc-001",
                generation_number=1,
                status=IndexGenerationStatus.COMPLETED,
                strategy="",
                chunk_count=10,
                is_active=True,
            )

    def test_invalid_negative_chunk_count(self):
        """Test that negative chunk_count raises ValueError."""
        with pytest.raises(ValueError, match="chunk_count must be >= 0"):
            IndexGeneration(
                id="gen-001",
                document_id="doc-001",
                generation_number=1,
                status=IndexGenerationStatus.COMPLETED,
                strategy="fixed_size",
                chunk_count=-1,
                is_active=True,
            )

    def test_different_statuses(self):
        """Test creating with different status values."""
        for status in [
            IndexGenerationStatus.IN_PROGRESS,
            IndexGenerationStatus.COMPLETED,
            IndexGenerationStatus.FAILED,
            IndexGenerationStatus.SUPERSEDED,
        ]:
            gen = IndexGeneration(
                id="gen-001",
                document_id="doc-001",
                generation_number=1,
                status=status,
                strategy="fixed_size",
                chunk_count=10,
                is_active=True,
            )
            assert gen.status == status

    def test_active_and_inactive_generations(self):
        """Test both active and inactive generations."""
        active_gen = IndexGeneration(
            id="gen-001",
            document_id="doc-001",
            generation_number=1,
            status=IndexGenerationStatus.COMPLETED,
            strategy="fixed_size",
            chunk_count=10,
            is_active=True,
        )
        assert active_gen.is_active is True

        inactive_gen = IndexGeneration(
            id="gen-002",
            document_id="doc-001",
            generation_number=0,
            status=IndexGenerationStatus.SUPERSEDED,
            strategy="fixed_size",
            chunk_count=10,
            is_active=False,
        )
        assert inactive_gen.is_active is False


class TestIndexEntry:
    """Test IndexEntry dataclass."""

    def test_create_index_entry(self):
        """Test creating a valid IndexEntry."""
        entry = IndexEntry(
            id="entry-001",
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id="doc-001",
            collection_id="col-001",
            generation_id="gen-001",
            chunk_order=0,
        )
        assert entry.id == "entry-001"
        assert entry.chunk_id == "chunk-001"
        assert entry.embedding_id == "emb-001"
        assert entry.document_id == "doc-001"
        assert entry.collection_id == "col-001"
        assert entry.generation_id == "gen-001"
        assert entry.chunk_order == 0
        assert entry.is_active is True  # default

    def test_create_with_optional_fields(self):
        """Test creating with optional fields."""
        entry = IndexEntry(
            id="entry-001",
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id="doc-001",
            collection_id="col-001",
            generation_id="gen-001",
            chunk_order=1,
            vector_db_id="vector-123",
            parent_chunk_id="chunk-000",
            created_at="2026-05-05T10:00:00",
            is_active=False,
        )
        assert entry.vector_db_id == "vector-123"
        assert entry.parent_chunk_id == "chunk-000"
        assert entry.created_at == "2026-05-05T10:00:00"
        assert entry.is_active is False

    def test_invalid_empty_id(self):
        """Test that empty id raises ValueError."""
        with pytest.raises(ValueError, match="id is required"):
            IndexEntry(
                id="",
                chunk_id="chunk-001",
                embedding_id="emb-001",
                document_id="doc-001",
                collection_id="col-001",
                generation_id="gen-001",
                chunk_order=0,
            )

    def test_invalid_empty_chunk_id(self):
        """Test that empty chunk_id raises ValueError."""
        with pytest.raises(ValueError, match="chunk_id is required"):
            IndexEntry(
                id="entry-001",
                chunk_id="",
                embedding_id="emb-001",
                document_id="doc-001",
                collection_id="col-001",
                generation_id="gen-001",
                chunk_order=0,
            )

    def test_invalid_empty_embedding_id(self):
        """Test that empty embedding_id raises ValueError."""
        with pytest.raises(ValueError, match="embedding_id is required"):
            IndexEntry(
                id="entry-001",
                chunk_id="chunk-001",
                embedding_id="",
                document_id="doc-001",
                collection_id="col-001",
                generation_id="gen-001",
                chunk_order=0,
            )

    def test_invalid_empty_document_id(self):
        """Test that empty document_id raises ValueError."""
        with pytest.raises(ValueError, match="document_id is required"):
            IndexEntry(
                id="entry-001",
                chunk_id="chunk-001",
                embedding_id="emb-001",
                document_id="",
                collection_id="col-001",
                generation_id="gen-001",
                chunk_order=0,
            )

    def test_invalid_empty_collection_id(self):
        """Test that empty collection_id raises ValueError."""
        with pytest.raises(ValueError, match="collection_id is required"):
            IndexEntry(
                id="entry-001",
                chunk_id="chunk-001",
                embedding_id="emb-001",
                document_id="doc-001",
                collection_id="",
                generation_id="gen-001",
                chunk_order=0,
            )

    def test_invalid_empty_generation_id(self):
        """Test that empty generation_id raises ValueError."""
        with pytest.raises(ValueError, match="generation_id is required"):
            IndexEntry(
                id="entry-001",
                chunk_id="chunk-001",
                embedding_id="emb-001",
                document_id="doc-001",
                collection_id="col-001",
                generation_id="",
                chunk_order=0,
            )

    def test_invalid_negative_chunk_order(self):
        """Test that negative chunk_order raises ValueError."""
        with pytest.raises(ValueError, match="chunk_order must be >= 0"):
            IndexEntry(
                id="entry-001",
                chunk_id="chunk-001",
                embedding_id="emb-001",
                document_id="doc-001",
                collection_id="col-001",
                generation_id="gen-001",
                chunk_order=-1,
            )

    def test_active_and_inactive_entries(self):
        """Test both active and inactive entries."""
        active_entry = IndexEntry(
            id="entry-001",
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id="doc-001",
            collection_id="col-001",
            generation_id="gen-001",
            chunk_order=0,
            is_active=True,
        )
        assert active_entry.is_active is True

        inactive_entry = IndexEntry(
            id="entry-002",
            chunk_id="chunk-002",
            embedding_id="emb-002",
            document_id="doc-001",
            collection_id="col-001",
            generation_id="gen-001",
            chunk_order=1,
            is_active=False,
        )
        assert inactive_entry.is_active is False

    def test_parent_child_entries(self):
        """Test entries with parent-child relationships."""
        parent_entry = IndexEntry(
            id="entry-parent",
            chunk_id="chunk-parent",
            embedding_id="emb-parent",
            document_id="doc-001",
            collection_id="col-001",
            generation_id="gen-001",
            chunk_order=0,
            parent_chunk_id=None,
        )
        assert parent_entry.parent_chunk_id is None

        child_entry = IndexEntry(
            id="entry-child",
            chunk_id="chunk-child",
            embedding_id="emb-child",
            document_id="doc-001",
            collection_id="col-001",
            generation_id="gen-001",
            chunk_order=1,
            parent_chunk_id="chunk-parent",
        )
        assert child_entry.parent_chunk_id == "chunk-parent"
