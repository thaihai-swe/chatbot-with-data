import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from migrations.runner import apply_migrations, reset_database
from repositories.core import Repository
from repositories.chunk_repository import ChunkRepository
from chunking.service import ChunkingService
from chunking.parent_child_chunker import ParentChildChunker


@pytest.fixture
def setup():
    """Setup test database and services."""
    reset_database()
    apply_migrations()

    repo = Repository()
    chunk_repo = ChunkRepository()
    chunking_service = ChunkingService()

    # Create test collection and document
    collection = repo.create_collection(
        name="parent_child_test",
        description="Parent-child chunking test"
    )

    document = repo.create_document(
        title="Parent-Child Test Document",
        source_type="md",
        source_uri=None,
        canonical_source_uri=None,
        filename="test.md",
        mime_type="text/markdown",
        file_hash="test_hash_pc",
        normalized_text_hash="test_norm_hash_pc",
        extracted_text="Test content",
        metadata={"test": True},
        collection_ids=[collection["id"]]
    )

    yield {
        "repo": repo,
        "chunk_repo": chunk_repo,
        "chunking_service": chunking_service,
        "collection": collection,
        "document": document,
    }

    reset_database()


def test_parent_child_chunker_basic(setup):
    """Test basic parent-child chunking strategy."""
    chunker = ParentChildChunker(chunk_size=30, children_per_parent=2)

    text = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five. Sentence six."
    chunks = chunker.chunk(text, title="Test Document")

    # Should have both child and parent chunks
    assert len(chunks) > 0

    # Check chunk structure
    for chunk in chunks:
        assert chunk.text
        assert chunk.title == "Test Document"
        assert hasattr(chunk, 'metadata')


def test_parent_child_chunker_grouping(setup):
    """Test that parent chunks are created from groups of children."""
    chunker = ParentChildChunker(chunk_size=25, children_per_parent=3)

    text = " ".join(["Sentence with content."] * 20)
    chunks = chunker.chunk(text)

    # Separate children and parents
    children = [c for c in chunks if not c.metadata.get("parent_chunk", False)]
    parents = [c for c in chunks if c.metadata.get("parent_chunk", False)]

    # Verify we have both
    assert len(children) > 0
    assert len(parents) > 0

    # Parents should be fewer than children (grouping of 3)
    assert len(parents) < len(children)


def test_parent_child_via_service(setup):
    """Test parent-child chunking through service layer."""
    service = setup["chunking_service"]
    doc = setup["document"]
    coll = setup["collection"]

    text = " ".join(["This is content here."] * 15)

    chunks = service.chunk_document(
        document_id=doc["id"],
        collection_id=coll["id"],
        text=text,
        strategy="parent_child",
        source_type="txt",
        chunk_size=25,
        metadata={"parent_child_test": True}
    )

    # Verify chunks were created
    assert len(chunks) > 0

    # Verify all chunks have correct document and collection
    for chunk in chunks:
        assert chunk["document_id"] == doc["id"]
        assert chunk["collection_id"] == coll["id"]


def test_parent_child_bidirectional_traversal(setup):
    """Test that parent-child relationships are queryable in both directions."""
    chunk_repo = setup["chunk_repo"]
    service = setup["chunking_service"]
    doc = setup["document"]
    coll = setup["collection"]

    text = " ".join(["Content sentence here."] * 12)

    # Generate chunks via service
    chunks = service.chunk_document(
        document_id=doc["id"],
        collection_id=coll["id"],
        text=text,
        strategy="parent_child",
        chunk_size=20,
        metadata={"test": "bidirectional"}
    )

    # Query all chunks by document
    db_chunks = chunk_repo.list_chunks_by_document(doc["id"])
    assert len(db_chunks) == len(chunks)

    # Separate children from parents
    children = [c for c in db_chunks if not c.get("metadata", {}).get("parent_chunk")]
    parents = [c for c in db_chunks if c.get("metadata", {}).get("parent_chunk")]

    # Test child->parent traversal
    for child in children:
        if child.get("parent_chunk_id"):
            parent = chunk_repo.get_chunk(child["parent_chunk_id"])
            assert parent is not None
            assert parent.get("metadata", {}).get("parent_chunk", False)


def test_parent_child_independent_queryability(setup):
    """Test that parent and child chunks are independently queryable."""
    chunk_repo = setup["chunk_repo"]
    service = setup["chunking_service"]
    doc = setup["document"]
    coll = setup["collection"]

    text = " ".join(["Document content here."] * 10)

    chunks = service.chunk_document(
        document_id=doc["id"],
        collection_id=coll["id"],
        text=text,
        strategy="parent_child",
        chunk_size=20
    )

    # Query by collection (both levels should be visible)
    collection_chunks = chunk_repo.list_chunks_by_collection(coll["id"])
    assert len(collection_chunks) > 0

    # Query by document (both levels should be visible)
    doc_chunks = chunk_repo.list_chunks_by_document(doc["id"])
    assert len(doc_chunks) > 0

    # Count should match
    assert len(collection_chunks) >= len(doc_chunks)


def test_parent_child_empty_text(setup):
    """Test parent-child chunking with empty text."""
    chunker = ParentChildChunker()

    chunks = chunker.chunk("")
    assert len(chunks) == 0

    chunks = chunker.chunk("   ")
    assert len(chunks) == 0


def test_parent_child_small_text(setup):
    """Test parent-child chunking with text smaller than chunk size."""
    chunker = ParentChildChunker(chunk_size=100, children_per_parent=2)

    text = "Short text."
    chunks = chunker.chunk(text)

    # Should still produce chunks (at least child chunks)
    assert len(chunks) > 0


def test_parent_child_deletion(setup):
    """Test that deleting document chunks removes both parents and children."""
    service = setup["chunking_service"]
    doc = setup["document"]
    coll = setup["collection"]

    text = " ".join(["Sample content."] * 8)

    chunks = service.chunk_document(
        document_id=doc["id"],
        collection_id=coll["id"],
        text=text,
        strategy="parent_child",
        chunk_size=20
    )

    assert len(chunks) > 0

    # Delete all chunks
    deleted_count = service.delete_document_chunks(doc["id"])
    assert deleted_count == len(chunks)

    # Verify all are gone
    remaining = service.get_document_chunks(doc["id"])
    assert len(remaining) == 0


def test_parent_child_chunker_direct_instantiation(setup):
    """Test ParentChildChunker can be instantiated and configured directly."""
    chunker1 = ParentChildChunker(chunk_size=512, children_per_parent=4)
    assert chunker1.chunk_size == 512
    assert chunker1.children_per_parent == 4

    chunker2 = ParentChildChunker(chunk_size=256, children_per_parent=2)
    assert chunker2.chunk_size == 256
    assert chunker2.children_per_parent == 2

    # Test with invalid children_per_parent (should clamp to >= 1)
    chunker3 = ParentChildChunker(children_per_parent=0)
    assert chunker3.children_per_parent == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
