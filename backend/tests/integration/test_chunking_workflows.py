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
        name="integration_test",
        description="Integration test collection"
    )

    document = repo.create_document(
        title="Integration Test Document",
        source_type="md",
        source_uri=None,
        canonical_source_uri=None,
        filename="test.md",
        mime_type="text/markdown",
        file_hash="test_hash",
        normalized_text_hash="test_norm_hash",
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


def test_end_to_end_chunking_workflow(setup):
    """Test complete chunking workflow."""
    service = setup["chunking_service"]
    doc = setup["document"]
    coll = setup["collection"]

    text = """
# Introduction
This is the introduction section with some content.

## Background
Here we provide background information.

# Main Content
This is the main content section.

## Details
Additional details go here.

# Conclusion
Final conclusions and remarks.
"""

    # Chunk document using heading-aware strategy
    chunks = service.chunk_document(
        document_id=doc["id"],
        collection_id=coll["id"],
        text=text,
        strategy="heading_aware",
        source_type="md",
        title=doc["title"],
        chunk_size=100,
        metadata={"strategy_test": "heading_aware"}
    )

    # Verify chunks were created
    assert len(chunks) > 0

    # Verify chunk properties
    for i, chunk in enumerate(chunks):
        assert chunk["document_id"] == doc["id"]
        assert chunk["collection_id"] == coll["id"]
        assert chunk["strategy"] == "heading_aware"
        assert len(chunk["text"]) > 0
        assert chunk["chunk_order"] == i + 1

    # Verify repository contains chunks
    db_chunks = setup["chunk_repo"].list_chunks_by_document(doc["id"])
    assert len(db_chunks) == len(chunks)

    # Verify chunk count
    count = service.count_document_chunks(doc["id"])
    assert count == len(chunks)


def test_fixed_size_chunking_integration(setup):
    """Test fixed-size chunking integration."""
    service = setup["chunking_service"]
    doc = setup["document"]
    coll = setup["collection"]

    long_text = " ".join(["This is a sentence."] * 50)

    chunks = service.chunk_document(
        document_id=doc["id"],
        collection_id=coll["id"],
        text=long_text,
        strategy="fixed_size",
        source_type="txt",
        chunk_size=30,
        overlap=0
    )

    assert len(chunks) > 1
    assert all(c["strategy"] == "fixed_size" for c in chunks)


def test_page_aware_chunking_integration(setup):
    """Test page-aware chunking integration."""
    service = setup["chunking_service"]
    doc = setup["document"]
    coll = setup["collection"]

    pdf_text = "Page 1 content here.###PAGE_BREAK###Page 2 content here.###PAGE_BREAK###Page 3 content here."

    chunks = service.chunk_document(
        document_id=doc["id"],
        collection_id=coll["id"],
        text=pdf_text,
        strategy="page_aware",
        source_type="pdf",
        chunk_size=50
    )

    assert len(chunks) > 0
    assert all(c["strategy"] == "page_aware" for c in chunks)


def test_delete_document_chunks(setup):
    """Test deleting all chunks for a document."""
    service = setup["chunking_service"]
    doc = setup["document"]
    coll = setup["collection"]

    text = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five."

    chunks = service.chunk_document(
        document_id=doc["id"],
        collection_id=coll["id"],
        text=text,
        strategy="fixed_size",
        chunk_size=20
    )

    assert len(chunks) > 0

    # Delete chunks
    count = service.delete_document_chunks(doc["id"])
    assert count == len(chunks)

    # Verify chunks are gone
    remaining = service.get_document_chunks(doc["id"])
    assert len(remaining) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
