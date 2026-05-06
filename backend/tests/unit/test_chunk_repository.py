import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from migrations.runner import apply_migrations, reset_database
from repositories.chunk_repository import ChunkRepository


@pytest.fixture
def repo():
    """Reset database and provide a repository instance."""
    reset_database()
    apply_migrations()

    # Create a test collection and document first
    from repositories.core import Repository
    main_repo = Repository()

    collection = main_repo.create_collection(
        name="test_collection",
        description="Test collection"
    )

    document = main_repo.create_document(
        title="Test Document",
        source_type="pdf",
        source_uri=None,
        canonical_source_uri=None,
        filename="test.pdf",
        mime_type="application/pdf",
        file_hash="abc123def456",
        normalized_text_hash="xyz789",
        extracted_text="This is test content",
        metadata={},
        collection_ids=[collection["id"]]
    )

    repo_instance = ChunkRepository()
    repo_instance.collection_id = collection["id"]
    repo_instance.document_id = document["id"]

    yield repo_instance

    # Cleanup
    reset_database()


def test_create_chunk(repo):
    """Test creating a chunk."""
    chunk = repo.create_chunk(
        document_id=repo.document_id,
        collection_id=repo.collection_id,
        chunk_order=1,
        strategy="fixed_size",
        source_type="pdf",
        title="Chapter 1",
        section_title="Introduction",
        page_number=1,
        source_url=None,
        text="This is the first chunk of content.",
        metadata={"key": "value"}
    )

    assert chunk is not None
    assert chunk["chunk_order"] == 1
    assert chunk["strategy"] == "fixed_size"
    assert chunk["text"] == "This is the first chunk of content."
    assert chunk["text_length"] == len("This is the first chunk of content.")
    assert chunk["metadata"]["key"] == "value"
    assert chunk["fallback_applied"] is False


def test_get_chunk(repo):
    """Test retrieving a chunk."""
    created = repo.create_chunk(
        document_id=repo.document_id,
        collection_id=repo.collection_id,
        chunk_order=1,
        strategy="fixed_size",
        source_type="pdf",
        title="Test",
        section_title=None,
        page_number=None,
        source_url=None,
        text="Chunk content"
    )

    retrieved = repo.get_chunk(created["id"])
    assert retrieved is not None
    assert retrieved["id"] == created["id"]
    assert retrieved["text"] == "Chunk content"


def test_list_chunks_by_document(repo):
    """Test listing chunks by document."""
    for i in range(3):
        repo.create_chunk(
            document_id=repo.document_id,
            collection_id=repo.collection_id,
            chunk_order=i + 1,
            strategy="fixed_size",
            source_type="pdf",
            title=f"Chunk {i+1}",
            section_title=None,
            page_number=None,
            source_url=None,
            text=f"Content {i+1}"
        )

    chunks = repo.list_chunks_by_document(repo.document_id)
    assert len(chunks) == 3
    assert chunks[0]["chunk_order"] == 1
    assert chunks[1]["chunk_order"] == 2
    assert chunks[2]["chunk_order"] == 3


def test_list_chunks_by_document_with_strategy_filter(repo):
    """Test listing chunks filtered by strategy."""
    # Create chunks with different strategies
    repo.create_chunk(
        document_id=repo.document_id,
        collection_id=repo.collection_id,
        chunk_order=1,
        strategy="fixed_size",
        source_type="pdf",
        title="Chunk 1",
        section_title=None,
        page_number=None,
        source_url=None,
        text="Content 1"
    )

    repo.create_chunk(
        document_id=repo.document_id,
        collection_id=repo.collection_id,
        chunk_order=2,
        strategy="heading_aware",
        source_type="pdf",
        title="Chunk 2",
        section_title=None,
        page_number=None,
        source_url=None,
        text="Content 2"
    )

    # Filter by strategy
    chunks = repo.list_chunks_by_document(repo.document_id, strategy="fixed_size")
    assert len(chunks) == 1
    assert chunks[0]["strategy"] == "fixed_size"


def test_update_chunk(repo):
    """Test updating a chunk."""
    chunk = repo.create_chunk(
        document_id=repo.document_id,
        collection_id=repo.collection_id,
        chunk_order=1,
        strategy="fixed_size",
        source_type="pdf",
        title="Original",
        section_title=None,
        page_number=None,
        source_url=None,
        text="Content",
        fallback_applied=False,
        semantic_score=None
    )

    updated = repo.update_chunk(
        chunk["id"],
        strategy="heading_aware",
        fallback_applied=True,
        semantic_score=0.95,
        metadata={"updated": True}
    )

    assert updated is not None
    assert updated["strategy"] == "heading_aware"
    assert updated["fallback_applied"] is True
    assert updated["semantic_score"] == 0.95
    assert updated["metadata"]["updated"] is True


def test_delete_chunk(repo):
    """Test deleting a chunk."""
    chunk = repo.create_chunk(
        document_id=repo.document_id,
        collection_id=repo.collection_id,
        chunk_order=1,
        strategy="fixed_size",
        source_type="pdf",
        title="To Delete",
        section_title=None,
        page_number=None,
        source_url=None,
        text="This will be deleted"
    )

    result = repo.delete_chunk(chunk["id"])
    assert result is True

    retrieved = repo.get_chunk(chunk["id"])
    assert retrieved is None


def test_delete_chunks_by_document(repo):
    """Test deleting all chunks for a document."""
    for i in range(3):
        repo.create_chunk(
            document_id=repo.document_id,
            collection_id=repo.collection_id,
            chunk_order=i + 1,
            strategy="fixed_size",
            source_type="pdf",
            title=f"Chunk {i+1}",
            section_title=None,
            page_number=None,
            source_url=None,
            text=f"Content {i+1}"
        )

    count = repo.delete_chunks_by_document(repo.document_id)
    assert count == 3

    chunks = repo.list_chunks_by_document(repo.document_id)
    assert len(chunks) == 0


def test_count_chunks_by_document(repo):
    """Test counting chunks for a document."""
    for i in range(5):
        repo.create_chunk(
            document_id=repo.document_id,
            collection_id=repo.collection_id,
            chunk_order=i + 1,
            strategy="fixed_size",
            source_type="pdf",
            title=f"Chunk {i+1}",
            section_title=None,
            page_number=None,
            source_url=None,
            text=f"Content {i+1}"
        )

    count = repo.count_chunks_by_document(repo.document_id)
    assert count == 5


def test_parent_child_chunks(repo):
    """Test parent-child chunk relationships."""
    # Create parent chunk
    parent = repo.create_chunk(
        document_id=repo.document_id,
        collection_id=repo.collection_id,
        chunk_order=1,
        strategy="parent_child",
        source_type="pdf",
        title="Parent",
        section_title=None,
        page_number=None,
        source_url=None,
        text="This is a parent chunk with multiple sub-sections"
    )

    # Create child chunks
    child1 = repo.create_chunk(
        document_id=repo.document_id,
        collection_id=repo.collection_id,
        chunk_order=2,
        strategy="parent_child",
        source_type="pdf",
        title="Child 1",
        section_title="Section 1",
        page_number=None,
        source_url=None,
        text="First child chunk",
        parent_chunk_id=parent["id"]
    )

    child2 = repo.create_chunk(
        document_id=repo.document_id,
        collection_id=repo.collection_id,
        chunk_order=3,
        strategy="parent_child",
        source_type="pdf",
        title="Child 2",
        section_title="Section 2",
        page_number=None,
        source_url=None,
        text="Second child chunk",
        parent_chunk_id=parent["id"]
    )

    # Verify parent-child relationships
    children = repo.get_chunks_by_parent_id(parent["id"])
    assert len(children) == 2
    assert children[0]["id"] == child1["id"]
    assert children[1]["id"] == child2["id"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
