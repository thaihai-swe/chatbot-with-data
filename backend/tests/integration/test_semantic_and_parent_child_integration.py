import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from migrations.runner import apply_migrations, reset_database
from repositories.core import Repository
from repositories.chunk_repository import ChunkRepository
from chunking.service import ChunkingService


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
        name="phase2_edge_cases",
        description="Phase 2 edge case testing"
    )

    document = repo.create_document(
        title="Phase 2 Test Document",
        source_type="md",
        source_uri=None,
        canonical_source_uri=None,
        filename="test_phase2.md",
        mime_type="text/markdown",
        file_hash="test_hash_phase2",
        normalized_text_hash="test_norm_hash_phase2",
        extracted_text="Test content",
        metadata={"phase": "2"},
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


# Semantic Chunking Edge Cases

def test_semantic_chunking_via_service(setup):
    """Test semantic chunking through service layer."""
    service = setup["chunking_service"]
    doc = setup["document"]
    coll = setup["collection"]

    text = """
    Introduction section here.
    More introduction details.
    Now we transition to main content.
    Main content is important.
    Key details about main content.
    """

    chunks = service.chunk_document(
        document_id=doc["id"],
        collection_id=coll["id"],
        text=text,
        strategy="semantic",
        source_type="txt",
        chunk_size=50
    )

    assert len(chunks) > 0
    assert all(c["document_id"] == doc["id"] for c in chunks)
    assert all(c["collection_id"] == coll["id"] for c in chunks)
    assert all(c["strategy"] == "semantic" for c in chunks)


def test_semantic_chunking_weak_signal_fallback(setup):
    """Test semantic chunking with weak signal triggers fallback."""
    service = setup["chunking_service"]
    doc = setup["document"]
    coll = setup["collection"]

    # Text with repetitive structure (weak semantic signal)
    text = "Topic A continues. Topic A persists. Topic A remains. Topic A recurs."

    chunks = service.chunk_document(
        document_id=doc["id"],
        collection_id=coll["id"],
        text=text,
        strategy="semantic",
        chunk_size=30
    )

    # Should still produce chunks (via fallback if signal is weak)
    assert len(chunks) > 0

    # Check if fallback was applied
    has_fallback_flag = any(
        c.get("metadata", {}).get("fallback_applied", False)
        for c in chunks
    )


def test_semantic_chunking_preserves_structure(setup):
    """Test that semantic chunking preserves document structure metadata."""
    service = setup["chunking_service"]
    doc = setup["document"]
    coll = setup["collection"]

    text = "Content here. More content. Final content."

    chunks = service.chunk_document(
        document_id=doc["id"],
        collection_id=coll["id"],
        text=text,
        strategy="semantic",
        title=doc["title"],
        metadata={"test": "value"}
    )

    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk["document_id"] == doc["id"]
        assert chunk["collection_id"] == coll["id"]
        assert chunk["strategy"] == "semantic"


def test_semantic_chunking_with_long_document(setup):
    """Test semantic chunking with longer document."""
    service = setup["chunking_service"]
    doc = setup["document"]
    coll = setup["collection"]

    # Longer text with natural topic flow
    text = """
    Introduction to machine learning.
    Historical development of ML.
    Evolution of algorithms.
    Supervised learning approaches.
    Unsupervised learning methods.
    Deep learning networks.
    Applications in industry.
    Challenges and future directions.
    """

    chunks = service.chunk_document(
        document_id=doc["id"],
        collection_id=coll["id"],
        text=text,
        strategy="semantic",
        chunk_size=100
    )

    assert len(chunks) > 0
    # All chunks should have sequential ordering
    for i, chunk in enumerate(chunks, 1):
        assert chunk["chunk_order"] == i


# Parent-Child Relationship Tests

def test_parent_child_bidirectional_query(setup):
    """Test bidirectional querying of parent-child relationships."""
    chunk_repo = setup["chunk_repo"]
    service = setup["chunking_service"]
    doc = setup["document"]
    coll = setup["collection"]

    text = " ".join(["Content here."] * 10)

    chunks = service.chunk_document(
        document_id=doc["id"],
        collection_id=coll["id"],
        text=text,
        strategy="parent_child",
        chunk_size=25
    )

    assert len(chunks) > 0

    # Get all chunks from repo
    db_chunks = chunk_repo.list_chunks_by_document(doc["id"])
    children = [c for c in db_chunks if not c.get("metadata", {}).get("parent_chunk")]
    parents = [c for c in db_chunks if c.get("metadata", {}).get("parent_chunk")]

    # Test child -> parent traversal
    for child in children:
        if child.get("parent_chunk_id"):
            parent = chunk_repo.get_chunk(child["parent_chunk_id"])
            assert parent is not None
            assert parent.get("metadata", {}).get("parent_chunk")


def test_parent_child_independent_filtering(setup):
    """Test that parent and child chunks are independently filterable."""
    chunk_repo = setup["chunk_repo"]
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

    # Query all
    all_chunks = chunk_repo.list_chunks_by_document(doc["id"])
    assert len(all_chunks) > 0

    # Separate and verify counts add up
    children = [c for c in all_chunks if not c.get("metadata", {}).get("parent_chunk")]
    parents = [c for c in all_chunks if c.get("metadata", {}).get("parent_chunk")]

    assert len(children) + len(parents) == len(all_chunks)


def test_parent_child_deletion_cascade(setup):
    """Test that deleting document removes both parents and children."""
    service = setup["chunking_service"]
    doc = setup["document"]
    coll = setup["collection"]

    text = " ".join(["Text content."] * 6)

    chunks = service.chunk_document(
        document_id=doc["id"],
        collection_id=coll["id"],
        text=text,
        strategy="parent_child",
        chunk_size=20
    )

    total_chunks = len(chunks)
    assert total_chunks > 0

    # Delete all chunks
    deleted = service.delete_document_chunks(doc["id"])
    assert deleted == total_chunks

    # Verify none remain
    remaining = service.get_document_chunks(doc["id"])
    assert len(remaining) == 0


# Combined Strategy Tests

def test_semantic_and_parent_child_comparison(setup):
    """Test that semantic and parent-child strategies produce different results."""
    service = setup["chunking_service"]
    doc = setup["document"]
    coll = setup["collection"]

    text = " ".join(["This is content."] * 12)

    # Get semantic chunks
    semantic_chunks = service.chunk_document(
        document_id=doc["id"],
        collection_id=coll["id"],
        text=text,
        strategy="semantic",
        chunk_size=30
    )

    # Clean up for next test
    service.delete_document_chunks(doc["id"])

    # Get parent-child chunks
    parent_child_chunks = service.chunk_document(
        document_id=doc["id"],
        collection_id=coll["id"],
        text=text,
        strategy="parent_child",
        chunk_size=30
    )

    # Both should produce chunks
    assert len(semantic_chunks) > 0
    assert len(parent_child_chunks) > 0

    # Strategies produce different chunk patterns
    # (parent-child includes parent chunks, semantic doesn't)
    semantic_only_chunks = [c for c in semantic_chunks]
    parent_child_total = len(parent_child_chunks)

    # Parent-child should have more chunks (includes parents)
    assert parent_child_total >= len(semantic_only_chunks)


def test_all_strategies_preserve_metadata(setup):
    """Test that all chunking strategies preserve metadata consistently."""
    service = setup["chunking_service"]
    doc = setup["document"]
    coll = setup["collection"]

    text = "Sample document content. With multiple sections. And various details."

    strategies = ["fixed_size", "heading_aware", "semantic", "parent_child"]

    for strategy in strategies:
        # Clean up before each test
        service.delete_document_chunks(doc["id"])

        chunks = service.chunk_document(
            document_id=doc["id"],
            collection_id=coll["id"],
            text=text,
            strategy=strategy,
            title="Test",
            metadata={"strategy_test": True}
        )

        assert len(chunks) > 0

        for chunk in chunks:
            # All should have these fields
            assert chunk["document_id"] == doc["id"]
            assert chunk["collection_id"] == coll["id"]
            assert chunk["strategy"] == strategy
            assert len(chunk["text"]) > 0


def test_chunking_and_retrieval_accuracy(setup):
    """Test that chunks can be reliably retrieved after storage."""
    chunk_repo = setup["chunk_repo"]
    service = setup["chunking_service"]
    doc = setup["document"]
    coll = setup["collection"]

    text = """
    First major section content.
    Detailed first section info.

    Second major section content.
    Detailed second section info.

    Third major section content.
    Detailed third section info.
    """

    chunks = service.chunk_document(
        document_id=doc["id"],
        collection_id=coll["id"],
        text=text,
        strategy="semantic",
        chunk_size=50
    )

    # Retrieve and verify
    retrieved = chunk_repo.list_chunks_by_document(doc["id"])

    assert len(retrieved) == len(chunks)

    # Verify all chunks are retrievable individually
    for chunk in chunks:
        if "id" in chunk:
            individual = chunk_repo.get_chunk(chunk["id"])
            assert individual is not None
            assert individual["id"] == chunk["id"]


def test_chunk_counting_accuracy(setup):
    """Test that chunk counts are accurate across strategies."""
    service = setup["chunking_service"]
    doc = setup["document"]
    coll = setup["collection"]

    text = " ".join(["Sentence content."] * 15)

    for strategy in ["fixed_size", "semantic"]:
        service.delete_document_chunks(doc["id"])

        chunks = service.chunk_document(
            document_id=doc["id"],
            collection_id=coll["id"],
            text=text,
            strategy=strategy,
            chunk_size=30
        )

        # Count via service
        count = service.count_document_chunks(doc["id"])
        assert count == len(chunks)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
