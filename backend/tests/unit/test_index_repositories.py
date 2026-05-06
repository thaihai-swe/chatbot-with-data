"""Unit tests for index generation and entry repositories."""
import pytest
import uuid

from migrations.runner import apply_migrations, reset_database
from models.enums import IndexGenerationStatus
from repositories.index_generation_repository import IndexGenerationRepository
from repositories.index_entry_repository import IndexEntryRepository
from database import get_connection


@pytest.fixture(autouse=True)
def _reset_db():
    """Reset database before each test."""
    reset_database()
    apply_migrations()
    yield


def _create_test_document(doc_id: str = "doc-001"):
    """Helper to create a test document."""
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO documents
            (id, title, source_type, extracted_text)
            VALUES (?, ?, ?, ?)
            """,
            (doc_id, f"Title for {doc_id}", "txt", f"Text for {doc_id}"),
        )


def _create_test_collection(col_id: str = "col-001"):
    """Helper to create a test collection."""
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO collections
            (id, name)
            VALUES (?, ?)
            """,
            (col_id, f"Collection {col_id}"),
        )


def _create_test_chunk(
    chunk_id: str = "chunk-001",
    doc_id: str = "doc-001",
    col_id: str = "col-001",
):
    """Helper to create a test chunk."""
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO chunks
            (id, document_id, collection_id, chunk_order, strategy, source_type, text, text_length)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                chunk_id,
                doc_id,
                col_id,
                0,
                "fixed_size",
                "txt",
                "Sample chunk text",
                18,
            ),
        )


def _create_test_embedding(
    emb_id: str = "emb-001",
    chunk_id: str = "chunk-001",
):
    """Helper to create a test embedding."""
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO embeddings
            (id, chunk_id, embedding_model, embedding_model_version, embedding_vector, input_text_hash)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                emb_id,
                chunk_id,
                "text-embedding-3-small",
                "1",
                b"\x00" * 100,  # Dummy embedding
                "hash-123",
            ),
        )


def _create_test_generation(
    doc_id: str = "doc-001",
    gen_num: int = 1,
    status: IndexGenerationStatus = IndexGenerationStatus.COMPLETED,
    strategy: str = "fixed_size",
    chunk_count: int = 5,
) -> str:
    """Helper to create a test generation and return its ID."""
    # Create document if it doesn't exist
    try:
        _create_test_document(doc_id)
    except Exception:
        pass  # Document may already exist

    gen_id = f"gen-{doc_id}-{gen_num}"
    IndexGenerationRepository.create_generation(
        id=gen_id,
        document_id=doc_id,
        generation_number=gen_num,
        status=status,
        strategy=strategy,
        chunk_count=chunk_count,
        settings_hash=f"hash-{gen_num}",
        embedding_model="text-embedding-3-small",
    )
    return gen_id


class TestIndexGenerationRepository:
    """Test IndexGenerationRepository."""

    def test_create_generation(self):
        """Test creating a generation."""
        gen_id = _create_test_generation()

        gen = IndexGenerationRepository.get_generation(gen_id)
        assert gen is not None
        assert gen.id == gen_id
        assert gen.document_id == "doc-001"
        assert gen.generation_number == 1
        assert gen.status == IndexGenerationStatus.COMPLETED
        assert gen.strategy == "fixed_size"
        assert gen.chunk_count == 5
        assert gen.is_active is True
        assert gen.settings_hash == "hash-1"
        assert gen.embedding_model == "text-embedding-3-small"

    def test_list_generations_by_document(self):
        """Test listing all generations for a document."""
        doc_id = "doc-001"
        gen1_id = _create_test_generation(doc_id=doc_id, gen_num=1)
        gen2_id = _create_test_generation(
            doc_id=doc_id, gen_num=2, chunk_count=10
        )

        gens = IndexGenerationRepository.list_generations_by_document(doc_id)
        assert len(gens) == 2
        # Should be ordered by generation_number DESC
        assert gens[0].generation_number == 2
        assert gens[1].generation_number == 1

    def test_list_generations_by_document_empty(self):
        """Test listing generations for a document with none."""
        gens = IndexGenerationRepository.list_generations_by_document("doc-999")
        assert len(gens) == 0

    def test_get_active_generation(self):
        """Test getting the active generation for a document."""
        doc_id = "doc-001"
        gen1_id = _create_test_generation(doc_id=doc_id, gen_num=1)

        active_gen = IndexGenerationRepository.get_active_generation(doc_id)
        assert active_gen is not None
        assert active_gen.id == gen1_id
        assert active_gen.is_active is True

    def test_get_active_generation_none(self):
        """Test getting active generation when none exist."""
        active_gen = IndexGenerationRepository.get_active_generation("doc-999")
        assert active_gen is None

    def test_update_status(self):
        """Test updating generation status."""
        gen_id = _create_test_generation()

        updated = IndexGenerationRepository.update_status(
            gen_id, IndexGenerationStatus.SUPERSEDED, completed_at="2026-05-05T10:00:00"
        )
        assert updated.status == IndexGenerationStatus.SUPERSEDED
        assert updated.completed_at == "2026-05-05T10:00:00"

    def test_mark_active(self):
        """Test marking a generation as active."""
        doc_id = "doc-001"
        gen1_id = _create_test_generation(doc_id=doc_id, gen_num=1)
        gen2_id = _create_test_generation(
            doc_id=doc_id, gen_num=2, status=IndexGenerationStatus.IN_PROGRESS
        )

        # Mark gen2 as active
        IndexGenerationRepository.mark_active(gen2_id)

        gen1 = IndexGenerationRepository.get_generation(gen1_id)
        gen2 = IndexGenerationRepository.get_generation(gen2_id)

        assert gen1.is_active is False
        assert gen2.is_active is True

    def test_mark_inactive(self):
        """Test marking a generation as inactive."""
        gen_id = _create_test_generation()
        assert IndexGenerationRepository.get_generation(gen_id).is_active is True

        IndexGenerationRepository.mark_inactive(gen_id)
        assert IndexGenerationRepository.get_generation(gen_id).is_active is False

    def test_delete_generation(self):
        """Test deleting a generation."""
        gen_id = _create_test_generation()

        IndexGenerationRepository.delete_generation(gen_id)
        assert IndexGenerationRepository.get_generation(gen_id) is None

    def test_delete_generations_by_document(self):
        """Test deleting all generations for a document."""
        doc_id = "doc-001"
        gen1_id = _create_test_generation(doc_id=doc_id, gen_num=1)
        gen2_id = _create_test_generation(doc_id=doc_id, gen_num=2)

        IndexGenerationRepository.delete_generations_by_document(doc_id)

        assert IndexGenerationRepository.get_generation(gen1_id) is None
        assert IndexGenerationRepository.get_generation(gen2_id) is None

    def test_count_generations_by_document(self):
        """Test counting generations for a document."""
        doc_id = "doc-001"
        _create_test_generation(doc_id=doc_id, gen_num=1)
        _create_test_generation(doc_id=doc_id, gen_num=2)

        count = IndexGenerationRepository.count_generations_by_document(doc_id)
        assert count == 2

    def test_count_generations_empty(self):
        """Test counting when no generations exist."""
        count = IndexGenerationRepository.count_generations_by_document("doc-999")
        assert count == 0


class TestIndexEntryRepository:
    """Test IndexEntryRepository."""

    def test_create_entry(self):
        """Test creating an index entry."""
        # Setup: Create document, collection, chunk, embedding, and generation
        _create_test_document("doc-001")
        _create_test_collection("col-001")
        _create_test_chunk("chunk-001", "doc-001", "col-001")
        _create_test_embedding("emb-001", "chunk-001")
        gen_id = _create_test_generation()

        entry_id = "entry-001"

        entry = IndexEntryRepository.create_entry(
            id=entry_id,
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=0,
            vector_db_id="vector-123",
        )

        assert entry.id == entry_id
        assert entry.chunk_id == "chunk-001"
        assert entry.embedding_id == "emb-001"
        assert entry.document_id == "doc-001"
        assert entry.collection_id == "col-001"
        assert entry.generation_id == gen_id
        assert entry.chunk_order == 0
        assert entry.vector_db_id == "vector-123"
        assert entry.is_active is True

    def test_create_entry_with_parent(self):
        """Test creating an entry with parent_chunk_id."""
        # Setup
        _create_test_document("doc-001")
        _create_test_collection("col-001")
        _create_test_chunk("chunk-child", "doc-001", "col-001")
        _create_test_chunk("chunk-parent", "doc-001", "col-001")
        _create_test_embedding("emb-child", "chunk-child")
        gen_id = _create_test_generation()

        entry = IndexEntryRepository.create_entry(
            id="entry-child",
            chunk_id="chunk-child",
            embedding_id="emb-child",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=1,
            parent_chunk_id="chunk-parent",
        )

        assert entry.parent_chunk_id == "chunk-parent"

    def test_list_entries_by_generation(self):
        """Test listing entries for a generation."""
        # Setup
        _create_test_document("doc-001")
        _create_test_collection("col-001")
        _create_test_chunk("chunk-001", "doc-001", "col-001")
        _create_test_chunk("chunk-002", "doc-001", "col-001")
        _create_test_embedding("emb-001", "chunk-001")
        _create_test_embedding("emb-002", "chunk-002")
        gen_id = _create_test_generation()

        IndexEntryRepository.create_entry(
            id="entry-001",
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=0,
        )

        IndexEntryRepository.create_entry(
            id="entry-002",
            chunk_id="chunk-002",
            embedding_id="emb-002",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=1,
        )

        entries = IndexEntryRepository.list_entries_by_generation(gen_id)
        assert len(entries) == 2
        assert entries[0].chunk_order == 0
        assert entries[1].chunk_order == 1

    def test_list_entries_by_document(self):
        """Test listing entries for a document."""
        # Setup
        doc_id = "doc-001"
        _create_test_document(doc_id)
        _create_test_collection("col-001")
        _create_test_chunk("chunk-001", doc_id, "col-001")
        _create_test_chunk("chunk-002", doc_id, "col-001")
        _create_test_embedding("emb-001", "chunk-001")
        _create_test_embedding("emb-002", "chunk-002")
        gen_id = _create_test_generation(doc_id=doc_id)

        IndexEntryRepository.create_entry(
            id="entry-001",
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id=doc_id,
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=0,
        )

        IndexEntryRepository.create_entry(
            id="entry-002",
            chunk_id="chunk-002",
            embedding_id="emb-002",
            document_id=doc_id,
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=1,
        )

        entries = IndexEntryRepository.list_entries_by_document(doc_id)
        assert len(entries) == 2

    def test_list_entries_by_document_active_only(self):
        """Test listing only active entries for a document."""
        # Setup
        doc_id = "doc-001"
        _create_test_document(doc_id)
        _create_test_collection("col-001")
        _create_test_chunk("chunk-001", doc_id, "col-001")
        _create_test_chunk("chunk-002", doc_id, "col-001")
        _create_test_embedding("emb-001", "chunk-001")
        _create_test_embedding("emb-002", "chunk-002")
        gen_id = _create_test_generation(doc_id=doc_id)

        entry1_id = "entry-001"
        entry2_id = "entry-002"

        IndexEntryRepository.create_entry(
            id=entry1_id,
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id=doc_id,
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=0,
            is_active=True,
        )

        IndexEntryRepository.create_entry(
            id=entry2_id,
            chunk_id="chunk-002",
            embedding_id="emb-002",
            document_id=doc_id,
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=1,
            is_active=False,
        )

        entries = IndexEntryRepository.list_entries_by_document(doc_id, active_only=True)
        assert len(entries) == 1
        assert entries[0].id == entry1_id

    def test_list_entries_by_collection(self):
        """Test listing entries for a collection."""
        # Setup
        _create_test_document("doc-001")
        col_id = "col-001"
        _create_test_collection(col_id)
        _create_test_chunk("chunk-001", "doc-001", col_id)
        _create_test_chunk("chunk-002", "doc-001", col_id)
        _create_test_embedding("emb-001", "chunk-001")
        _create_test_embedding("emb-002", "chunk-002")
        gen_id = _create_test_generation()

        IndexEntryRepository.create_entry(
            id="entry-001",
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id="doc-001",
            collection_id=col_id,
            generation_id=gen_id,
            chunk_order=0,
        )

        IndexEntryRepository.create_entry(
            id="entry-002",
            chunk_id="chunk-002",
            embedding_id="emb-002",
            document_id="doc-001",
            collection_id=col_id,
            generation_id=gen_id,
            chunk_order=1,
        )

        entries = IndexEntryRepository.list_entries_by_collection(col_id)
        assert len(entries) == 2

    def test_list_entries_by_chunk(self):
        """Test listing entries for a chunk."""
        # Setup
        _create_test_document("doc-001")
        _create_test_collection("col-001")
        chunk_id = "chunk-001"
        _create_test_chunk(chunk_id, "doc-001", "col-001")
        _create_test_embedding("emb-001", chunk_id)
        gen_id = _create_test_generation()

        IndexEntryRepository.create_entry(
            id="entry-001",
            chunk_id=chunk_id,
            embedding_id="emb-001",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=0,
        )

        entries = IndexEntryRepository.list_entries_by_chunk(chunk_id)
        assert len(entries) == 1
        assert entries[0].chunk_id == chunk_id

    def test_update_is_active(self):
        """Test updating the is_active flag."""
        # Setup
        _create_test_document("doc-001")
        _create_test_collection("col-001")
        _create_test_chunk("chunk-001", "doc-001", "col-001")
        _create_test_embedding("emb-001", "chunk-001")
        gen_id = _create_test_generation()
        entry_id = "entry-001"

        IndexEntryRepository.create_entry(
            id=entry_id,
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=0,
            is_active=True,
        )

        entry = IndexEntryRepository.update_is_active(entry_id, False)
        assert entry.is_active is False

    def test_mark_generation_inactive(self):
        """Test marking all entries for a generation as inactive."""
        # Setup
        _create_test_document("doc-001")
        _create_test_collection("col-001")
        _create_test_chunk("chunk-001", "doc-001", "col-001")
        _create_test_chunk("chunk-002", "doc-001", "col-001")
        _create_test_embedding("emb-001", "chunk-001")
        _create_test_embedding("emb-002", "chunk-002")
        gen_id = _create_test_generation()

        IndexEntryRepository.create_entry(
            id="entry-001",
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=0,
            is_active=True,
        )

        IndexEntryRepository.create_entry(
            id="entry-002",
            chunk_id="chunk-002",
            embedding_id="emb-002",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=1,
            is_active=True,
        )

        IndexEntryRepository.mark_generation_inactive(gen_id)

        entries = IndexEntryRepository.list_entries_by_generation(gen_id)
        assert all(not entry.is_active for entry in entries)

    def test_mark_document_entries_active(self):
        """Test switching active generation for a document."""
        # Setup
        doc_id = "doc-001"
        _create_test_document(doc_id)
        _create_test_collection("col-001")
        _create_test_chunk("chunk-001", doc_id, "col-001")
        _create_test_chunk("chunk-002", doc_id, "col-001")
        _create_test_embedding("emb-001", "chunk-001")
        _create_test_embedding("emb-002", "chunk-002")
        gen1_id = _create_test_generation(doc_id=doc_id, gen_num=1)
        gen2_id = _create_test_generation(doc_id=doc_id, gen_num=2)

        # Create entries for both generations
        IndexEntryRepository.create_entry(
            id="entry-gen1",
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id=doc_id,
            collection_id="col-001",
            generation_id=gen1_id,
            chunk_order=0,
            is_active=True,
        )

        IndexEntryRepository.create_entry(
            id="entry-gen2",
            chunk_id="chunk-002",
            embedding_id="emb-002",
            document_id=doc_id,
            collection_id="col-001",
            generation_id=gen2_id,
            chunk_order=0,
            is_active=False,
        )

        # Activate gen2
        IndexEntryRepository.mark_document_entries_active(doc_id, gen2_id)

        entries = IndexEntryRepository.list_entries_by_document(doc_id)
        assert entries[0].is_active is False
        assert entries[1].is_active is True

    def test_delete_entry(self):
        """Test deleting an entry."""
        # Setup
        _create_test_document("doc-001")
        _create_test_collection("col-001")
        _create_test_chunk("chunk-001", "doc-001", "col-001")
        _create_test_embedding("emb-001", "chunk-001")
        gen_id = _create_test_generation()
        entry_id = "entry-001"

        IndexEntryRepository.create_entry(
            id=entry_id,
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=0,
        )

        IndexEntryRepository.delete_entry(entry_id)
        assert IndexEntryRepository.get_entry(entry_id) is None

    def test_delete_entries_by_generation(self):
        """Test deleting all entries for a generation."""
        # Setup
        _create_test_document("doc-001")
        _create_test_collection("col-001")
        _create_test_chunk("chunk-001", "doc-001", "col-001")
        _create_test_embedding("emb-001", "chunk-001")
        gen_id = _create_test_generation()

        IndexEntryRepository.create_entry(
            id="entry-001",
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=0,
        )

        IndexEntryRepository.delete_entries_by_generation(gen_id)
        entries = IndexEntryRepository.list_entries_by_generation(gen_id)
        assert len(entries) == 0

    def test_delete_entries_by_document(self):
        """Test deleting all entries for a document."""
        # Setup
        _create_test_document("doc-001")
        _create_test_collection("col-001")
        _create_test_chunk("chunk-001", "doc-001", "col-001")
        _create_test_embedding("emb-001", "chunk-001")
        gen_id = _create_test_generation()

        IndexEntryRepository.create_entry(
            id="entry-001",
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=0,
        )

        IndexEntryRepository.delete_entries_by_document("doc-001")
        entries = IndexEntryRepository.list_entries_by_document("doc-001")
        assert len(entries) == 0

    def test_delete_entries_by_collection(self):
        """Test deleting all entries for a collection."""
        # Setup
        _create_test_document("doc-001")
        _create_test_collection("col-001")
        _create_test_chunk("chunk-001", "doc-001", "col-001")
        _create_test_embedding("emb-001", "chunk-001")
        gen_id = _create_test_generation()

        IndexEntryRepository.create_entry(
            id="entry-001",
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=0,
        )

        IndexEntryRepository.delete_entries_by_collection("col-001")
        entries = IndexEntryRepository.list_entries_by_collection("col-001")
        assert len(entries) == 0

    def test_count_entries_by_generation(self):
        """Test counting entries for a generation."""
        # Setup
        _create_test_document("doc-001")
        _create_test_collection("col-001")
        _create_test_chunk("chunk-001", "doc-001", "col-001")
        _create_test_chunk("chunk-002", "doc-001", "col-001")
        _create_test_embedding("emb-001", "chunk-001")
        _create_test_embedding("emb-002", "chunk-002")
        gen_id = _create_test_generation()

        IndexEntryRepository.create_entry(
            id="entry-001",
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=0,
        )

        IndexEntryRepository.create_entry(
            id="entry-002",
            chunk_id="chunk-002",
            embedding_id="emb-002",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=1,
        )

        count = IndexEntryRepository.count_entries_by_generation(gen_id)
        assert count == 2

    def test_count_entries_by_document(self):
        """Test counting entries for a document."""
        # Setup
        _create_test_document("doc-001")
        _create_test_collection("col-001")
        _create_test_chunk("chunk-001", "doc-001", "col-001")
        _create_test_chunk("chunk-002", "doc-001", "col-001")
        _create_test_embedding("emb-001", "chunk-001")
        _create_test_embedding("emb-002", "chunk-002")
        gen_id = _create_test_generation()

        IndexEntryRepository.create_entry(
            id="entry-001",
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=0,
        )

        IndexEntryRepository.create_entry(
            id="entry-002",
            chunk_id="chunk-002",
            embedding_id="emb-002",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=1,
        )

        count = IndexEntryRepository.count_entries_by_document("doc-001")
        assert count == 2

    def test_count_entries_by_document_active_only(self):
        """Test counting active entries for a document."""
        # Setup
        _create_test_document("doc-001")
        _create_test_collection("col-001")
        _create_test_chunk("chunk-001", "doc-001", "col-001")
        _create_test_chunk("chunk-002", "doc-001", "col-001")
        _create_test_embedding("emb-001", "chunk-001")
        _create_test_embedding("emb-002", "chunk-002")
        gen_id = _create_test_generation()

        IndexEntryRepository.create_entry(
            id="entry-001",
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=0,
            is_active=True,
        )

        IndexEntryRepository.create_entry(
            id="entry-002",
            chunk_id="chunk-002",
            embedding_id="emb-002",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=1,
            is_active=False,
        )

        count = IndexEntryRepository.count_entries_by_document("doc-001", active_only=True)
        assert count == 1

    def test_count_entries_by_collection(self):
        """Test counting entries for a collection."""
        # Setup
        _create_test_document("doc-001")
        _create_test_collection("col-001")
        _create_test_chunk("chunk-001", "doc-001", "col-001")
        _create_test_embedding("emb-001", "chunk-001")
        gen_id = _create_test_generation()

        IndexEntryRepository.create_entry(
            id="entry-001",
            chunk_id="chunk-001",
            embedding_id="emb-001",
            document_id="doc-001",
            collection_id="col-001",
            generation_id=gen_id,
            chunk_order=0,
        )

        count = IndexEntryRepository.count_entries_by_collection("col-001")
        assert count == 1
