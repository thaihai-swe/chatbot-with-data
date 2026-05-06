import sys
from pathlib import Path
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest

from indexing.chroma_writer import ChromaVectorWriter


@pytest.fixture(scope="function")
def temp_chroma_dir():
    """Create a temporary directory for Chroma persistence."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def chroma_writer(temp_chroma_dir):
    """Create a Chroma writer instance for testing."""
    return ChromaVectorWriter(
        persist_directory=temp_chroma_dir,
        collection_name="test-chunks",
    )


@pytest.fixture
def sample_vector():
    """Sample embedding vector."""
    return [0.1, 0.2, 0.3] + [0.0] * 1533  # 1536 dims


@pytest.fixture
def sample_metadata():
    """Sample metadata for a vector."""
    return {
        "chunk_id": "chunk-001",
        "document_id": "doc-001",
        "collection_id": "col-001",
        "chunk_order": 0,
        "source_url": "https://example.com/doc.pdf",
        "page_number": 1,
        "section_title": "Introduction",
    }


class TestChromaVectorWriter:
    """Test Chroma vector writer operations."""

    def test_initialization(self, chroma_writer):
        """Test writer initialization."""
        assert chroma_writer.collection_name == "test-chunks"
        assert chroma_writer.client is not None
        assert chroma_writer.collection is not None

    def test_add_single_vector(self, chroma_writer, sample_vector, sample_metadata):
        """Test adding a single vector."""
        vector_id = "vector-001"

        result = chroma_writer.add_vector(
            vector_id=vector_id,
            embedding=sample_vector,
            metadata=sample_metadata,
        )

        assert result == vector_id
        assert chroma_writer.count_vectors() == 1

    def test_add_vector_missing_metadata(self, chroma_writer, sample_vector):
        """Test that adding vector with incomplete metadata fails."""
        with pytest.raises(ValueError, match="missing required keys"):
            chroma_writer.add_vector(
                vector_id="vector-001",
                embedding=sample_vector,
                metadata={"chunk_id": "chunk-001"},  # Missing required fields
            )

    def test_add_multiple_vectors_batch(self, chroma_writer, sample_vector, sample_metadata):
        """Test batch adding vectors."""
        vectors_data = [
            ("vector-001", sample_vector, {**sample_metadata, "chunk_id": "chunk-001"}),
            ("vector-002", sample_vector, {**sample_metadata, "chunk_id": "chunk-002"}),
            ("vector-003", sample_vector, {**sample_metadata, "chunk_id": "chunk-003"}),
        ]

        count = chroma_writer.add_vectors_batch(vectors_data)

        assert count == 3
        assert chroma_writer.count_vectors() == 3

    def test_query_vectors(self, chroma_writer, sample_vector, sample_metadata):
        """Test querying vectors."""
        # Add some vectors
        vectors_data = [
            ("vector-001", sample_vector, {**sample_metadata, "chunk_id": "chunk-001"}),
            ("vector-002", sample_vector, {**sample_metadata, "chunk_id": "chunk-002"}),
        ]
        chroma_writer.add_vectors_batch(vectors_data)

        # Query with same vector
        results = chroma_writer.query(
            query_embedding=sample_vector,
            n_results=2,
        )

        assert results is not None
        assert len(results['ids'][0]) > 0
        assert len(results['metadatas'][0]) > 0

    def test_query_with_collection_filter(self, chroma_writer, sample_vector):
        """Test collection-aware filtering in queries."""
        metadata1 = {
            "chunk_id": "chunk-001",
            "document_id": "doc-001",
            "collection_id": "col-001",
            "chunk_order": 0,
        }

        metadata2 = {
            "chunk_id": "chunk-002",
            "document_id": "doc-002",
            "collection_id": "col-002",
            "chunk_order": 0,
        }

        # Add vectors with different collection IDs
        chroma_writer.add_vector("vector-001", sample_vector, metadata1)
        chroma_writer.add_vector("vector-002", sample_vector, metadata2)

        # Query filtered by collection
        results = chroma_writer.query(
            query_embedding=sample_vector,
            n_results=10,
            collection_filter="col-001",
        )

        # Should only get results from col-001
        assert len(results['ids'][0]) > 0
        for metadata in results['metadatas'][0]:
            assert metadata['collection_id'] == "col-001"

    def test_query_by_collection(self, chroma_writer, sample_vector):
        """Test query_by_collection convenience method."""
        metadata = {
            "chunk_id": "chunk-001",
            "document_id": "doc-001",
            "collection_id": "col-001",
            "chunk_order": 0,
        }

        chroma_writer.add_vector("vector-001", sample_vector, metadata)

        results = chroma_writer.query_by_collection(
            query_embedding=sample_vector,
            collection_id="col-001",
            n_results=10,
        )

        assert len(results) > 0
        # Returns (chunk_id, similarity, metadata) tuples
        chunk_id, similarity, result_metadata = results[0]
        assert chunk_id == "chunk-001"
        assert 0 <= similarity <= 2  # Cosine similarity can be > 1 in some cases
        assert result_metadata['collection_id'] == "col-001"

    def test_get_vector(self, chroma_writer, sample_vector, sample_metadata):
        """Test retrieving a specific vector."""
        vector_id = "vector-001"
        chroma_writer.add_vector(vector_id, sample_vector, sample_metadata)

        retrieved = chroma_writer.get_vector(vector_id)

        assert retrieved is not None
        assert retrieved['embedding'] is not None
        assert retrieved['metadata']['chunk_id'] == "chunk-001"

    def test_get_nonexistent_vector(self, chroma_writer):
        """Test retrieving vector that doesn't exist."""
        retrieved = chroma_writer.get_vector("nonexistent")
        assert retrieved is None

    def test_delete_vector(self, chroma_writer, sample_vector, sample_metadata):
        """Test deleting a vector."""
        vector_id = "vector-001"
        chroma_writer.add_vector(vector_id, sample_vector, sample_metadata)

        assert chroma_writer.count_vectors() == 1

        deleted = chroma_writer.delete_vector(vector_id)
        assert deleted is True
        assert chroma_writer.count_vectors() == 0

    def test_delete_by_document(self, chroma_writer, sample_vector, sample_metadata):
        """Test deleting all vectors for a document."""
        # Add vectors for two documents
        metadata_doc1 = {**sample_metadata, "document_id": "doc-001"}
        metadata_doc2 = {**sample_metadata, "document_id": "doc-002"}

        chroma_writer.add_vector("vector-001", sample_vector, metadata_doc1)
        chroma_writer.add_vector("vector-002", sample_vector, metadata_doc1)
        chroma_writer.add_vector("vector-003", sample_vector, metadata_doc2)

        assert chroma_writer.count_vectors() == 3

        # Delete doc-001 vectors
        count = chroma_writer.delete_by_document("doc-001")

        assert count == 2
        assert chroma_writer.count_vectors() == 1

    def test_delete_by_collection(self, chroma_writer, sample_vector, sample_metadata):
        """Test deleting all vectors for a collection."""
        # Add vectors for two collections
        metadata_col1 = {**sample_metadata, "collection_id": "col-001"}
        metadata_col2 = {**sample_metadata, "collection_id": "col-002"}

        chroma_writer.add_vector("vector-001", sample_vector, metadata_col1)
        chroma_writer.add_vector("vector-002", sample_vector, metadata_col1)
        chroma_writer.add_vector("vector-003", sample_vector, metadata_col2)

        assert chroma_writer.count_vectors() == 3

        # Delete col-001 vectors
        count = chroma_writer.delete_by_collection("col-001")

        assert count == 2
        assert chroma_writer.count_vectors() == 1

    def test_count_vectors(self, chroma_writer, sample_vector, sample_metadata):
        """Test vector counting."""
        assert chroma_writer.count_vectors() == 0

        chroma_writer.add_vector("vector-001", sample_vector, sample_metadata)
        assert chroma_writer.count_vectors() == 1

        chroma_writer.add_vector("vector-002", sample_vector, sample_metadata)
        assert chroma_writer.count_vectors() == 2

    def test_clear_collection(self, chroma_writer, sample_vector, sample_metadata):
        """Test clearing all vectors from collection."""
        chroma_writer.add_vector("vector-001", sample_vector, sample_metadata)
        assert chroma_writer.count_vectors() == 1

        chroma_writer.clear_collection()
        assert chroma_writer.count_vectors() == 0

    def test_get_collection_stats(self, chroma_writer, sample_vector, sample_metadata):
        """Test retrieving collection statistics."""
        chroma_writer.add_vector("vector-001", sample_vector, sample_metadata)

        stats = chroma_writer.get_collection_stats()

        assert stats['collection_name'] == "test-chunks"
        assert stats['vector_count'] == 1
        assert stats['metadata'] is not None

    def test_metadata_preservation(self, chroma_writer, sample_vector):
        """Test that all metadata is preserved through add and retrieve."""
        metadata = {
            "chunk_id": "chunk-001",
            "document_id": "doc-001",
            "collection_id": "col-001",
            "chunk_order": 5,
            "source_url": "https://example.com/doc.pdf",
            "page_number": 42,
            "section_title": "Chapter 3",
            "parent_chunk_id": "parent-001",
        }

        vector_id = "vector-001"
        chroma_writer.add_vector(vector_id, sample_vector, metadata)

        retrieved = chroma_writer.get_vector(vector_id)

        # Verify all metadata fields are preserved
        for key, value in metadata.items():
            assert retrieved['metadata'][key] == value


class TestChromaIntegration:
    """Integration tests for Chroma with multiple operations."""

    def test_multi_document_multi_collection(self, chroma_writer, sample_vector):
        """Test indexing vectors from multiple documents and collections."""
        # Simulate documents from multiple collections
        vectors_data = []

        for doc_id in ["doc-001", "doc-002"]:
            for col_id in ["col-A", "col-B"]:
                for chunk_id in ["chunk-1", "chunk-2"]:
                    vector_id = f"v-{doc_id}-{col_id}-{chunk_id}"
                    metadata = {
                        "chunk_id": chunk_id,
                        "document_id": doc_id,
                        "collection_id": col_id,
                        "chunk_order": 0,
                    }
                    vectors_data.append((vector_id, sample_vector, metadata))

        # Add all vectors
        count = chroma_writer.add_vectors_batch(vectors_data)
        assert count == 8  # 2 docs * 2 cols * 2 chunks

        # Query by collection - should get 4 vectors (2 docs * 2 chunks per collection)
        results = chroma_writer.query_by_collection(
            query_embedding=sample_vector,
            collection_id="col-A",
            n_results=10,
        )

        assert len(results) == 4
        for chunk_id, similarity, metadata in results:
            assert metadata['collection_id'] == "col-A"

    def test_parent_child_metadata(self, chroma_writer, sample_vector):
        """Test that parent-child relationships are preserved."""
        parent_metadata = {
            "chunk_id": "parent-chunk",
            "document_id": "doc-001",
            "collection_id": "col-001",
            "chunk_order": 0,
        }

        child_metadata = {
            "chunk_id": "child-chunk",
            "document_id": "doc-001",
            "collection_id": "col-001",
            "chunk_order": 1,
            "parent_chunk_id": "parent-chunk",
        }

        chroma_writer.add_vector("vector-parent", sample_vector, parent_metadata)
        chroma_writer.add_vector("vector-child", sample_vector, child_metadata)

        # Retrieve and verify relationships
        parent = chroma_writer.get_vector("vector-parent")
        child = chroma_writer.get_vector("vector-child")

        # Parent doesn't have parent_chunk_id since it's None (filtered out by sanitization)
        assert "parent_chunk_id" not in parent['metadata']
        # Child has parent_chunk_id
        assert child['metadata']['parent_chunk_id'] == "parent-chunk"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
