from __future__ import annotations

import uuid
import pytest
from database import get_connection
from repositories import DocumentRepository

@pytest.fixture
def test_setup():
    parent_id = str(uuid.uuid4())
    child_id = str(uuid.uuid4())
    
    with get_connection() as conn:
        # Seed parent document
        conn.execute(
            "INSERT INTO documents (id, title, source_type, extracted_text) VALUES (?, ?, ?, ?)",
            (parent_id, "Parent Doc", "manual", "parent content"),
        )
        # Seed child document pointing to parent as a version of it
        conn.execute(
            "INSERT INTO documents (id, title, source_type, extracted_text, version_of_document_id) VALUES (?, ?, ?, ?, ?)",
            (child_id, "Child Doc Version", "manual", "child content", parent_id),
        )
        
    return {
        "parent_id": parent_id,
        "child_id": child_id,
    }

def test_delete_document_with_versions(test_setup):
    doc_repo = DocumentRepository()
    parent_id = test_setup["parent_id"]
    child_id = test_setup["child_id"]
    
    # Pre-flight check: assert child points to parent
    with get_connection() as conn:
        row = conn.execute("SELECT version_of_document_id FROM documents WHERE id = ?", (child_id,)).fetchone()
        assert row["version_of_document_id"] == parent_id
        
    # Act: delete parent document
    success = doc_repo.delete_document(parent_id)
    assert success is True
    
    # Assert: child version reference is updated to NULL, and parent is deleted
    with get_connection() as conn:
        parent_row = conn.execute("SELECT * FROM documents WHERE id = ?", (parent_id,)).fetchone()
        assert parent_row is None
        
        child_row = conn.execute("SELECT version_of_document_id FROM documents WHERE id = ?", (child_id,)).fetchone()
        assert child_row["version_of_document_id"] is None


def test_delete_collection_hard_purges_in_sqlite():
    from repositories import CollectionRepository
    from repositories.chunk_repository import ChunkRepository
    coll_repo = CollectionRepository()
    chunk_repo = ChunkRepository()
    
    coll_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    chunk_id = str(uuid.uuid4())
    
    with get_connection() as conn:
        conn.execute("INSERT INTO collections (id, name) VALUES (?, ?)", (coll_id, f"test-coll-{coll_id}"))
        conn.execute(
            "INSERT INTO documents (id, title, source_type, extracted_text) VALUES (?, ?, ?, ?)",
            (doc_id, "Test Doc", "manual", "test text"),
        )
        conn.execute(
            "INSERT INTO document_collections (document_id, collection_id) VALUES (?, ?)",
            (doc_id, coll_id),
        )
        conn.execute(
            "INSERT INTO chunks (id, document_id, collection_id, chunk_order, strategy, source_type, text, text_length) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (chunk_id, doc_id, coll_id, 0, "test", "manual", "test", 4),
        )
        
    # Pre-flight check: records exist
    with get_connection() as conn:
        assert conn.execute("SELECT * FROM collections WHERE id = ?", (coll_id,)).fetchone() is not None
        assert conn.execute("SELECT * FROM document_collections WHERE collection_id = ?", (coll_id,)).fetchone() is not None
        assert conn.execute("SELECT * FROM chunks WHERE collection_id = ?", (coll_id,)).fetchone() is not None
        
    # Act: delete collection
    success = coll_repo.delete_collection(coll_id)
    assert success is True
    
    # Assert: records are completely purged (hard deleted) from SQLite
    with get_connection() as conn:
        assert conn.execute("SELECT * FROM collections WHERE id = ?", (coll_id,)).fetchone() is None
        assert conn.execute("SELECT * FROM document_collections WHERE collection_id = ?", (coll_id,)).fetchone() is None
        assert conn.execute("SELECT * FROM chunks WHERE collection_id = ?", (coll_id,)).fetchone() is None


def test_delete_collection_endpoint_triggers_vector_purge(mocker):
    mock_store_class = mocker.patch("indexing.weaviate_store.WeaviateVectorStore")
    mock_store_instance = mock_store_class.return_value
    mock_store_instance.delete_by_collection.return_value = 1
    mocker.patch("ingestion.service.WeaviateVectorStore", mock_store_class)
    
    from fastapi.testclient import TestClient
    from app import app
    
    coll_id = str(uuid.uuid4())
    with get_connection() as conn:
        conn.execute("INSERT INTO collections (id, name) VALUES (?, ?)", (coll_id, f"test-coll-{coll_id}"))
        
    client = TestClient(app)
    resp = client.delete(f"/collections/{coll_id}")
    assert resp.status_code == 204
    
    # Verify collection hard deleted in SQLite
    with get_connection() as conn:
        assert conn.execute("SELECT * FROM collections WHERE id = ?", (coll_id,)).fetchone() is None
        
    # Verify vector store delete_by_collection called
    mock_store_instance.delete_by_collection.assert_called_once_with(coll_id)


def test_delete_collection_purges_orphan_documents(mocker):
    mock_store_class = mocker.patch("indexing.weaviate_store.WeaviateVectorStore")
    mock_store_instance = mock_store_class.return_value
    mock_store_instance.delete_by_collection.return_value = 1
    mock_store_instance.delete_by_document.return_value = 1
    mocker.patch("ingestion.service.WeaviateVectorStore", mock_store_class)
    
    from fastapi.testclient import TestClient
    from app import app
    
    coll_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    
    with get_connection() as conn:
        conn.execute("INSERT INTO collections (id, name) VALUES (?, ?)", (coll_id, f"test-coll-{coll_id}"))
        conn.execute(
            "INSERT INTO documents (id, title, source_type, extracted_text) VALUES (?, ?, ?, ?)",
            (doc_id, "Test Doc", "manual", "test text"),
        )
        conn.execute(
            "INSERT INTO document_collections (document_id, collection_id) VALUES (?, ?)",
            (doc_id, coll_id),
        )
        
    client = TestClient(app)
    resp = client.delete(f"/collections/{coll_id}")
    assert resp.status_code == 204
    
    with get_connection() as conn:
        # Collection and orphan document are deleted
        assert conn.execute("SELECT * FROM collections WHERE id = ?", (coll_id,)).fetchone() is None
        assert conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone() is None
        
    # Verify both vector store deletes were triggered
    mock_store_instance.delete_by_collection.assert_called_once_with(coll_id)
    mock_store_instance.delete_by_document.assert_called_once_with(doc_id)


def test_delete_collection_preserves_shared_documents(mocker):
    mock_store_class = mocker.patch("indexing.weaviate_store.WeaviateVectorStore")
    mock_store_instance = mock_store_class.return_value
    mock_store_instance.delete_by_collection.return_value = 1
    mock_store_instance.delete_by_document.return_value = 1
    mocker.patch("ingestion.service.WeaviateVectorStore", mock_store_class)
    
    from fastapi.testclient import TestClient
    from app import app
    
    coll1_id = str(uuid.uuid4())
    coll2_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    
    with get_connection() as conn:
        conn.execute("INSERT INTO collections (id, name) VALUES (?, ?)", (coll1_id, f"test-coll-{coll1_id}"))
        conn.execute("INSERT INTO collections (id, name) VALUES (?, ?)", (coll2_id, f"test-coll-{coll2_id}"))
        conn.execute(
            "INSERT INTO documents (id, title, source_type, extracted_text) VALUES (?, ?, ?, ?)",
            (doc_id, "Test Doc", "manual", "test text"),
        )
        conn.execute(
            "INSERT INTO document_collections (document_id, collection_id) VALUES (?, ?)",
            (doc_id, coll1_id),
        )
        conn.execute(
            "INSERT INTO document_collections (document_id, collection_id) VALUES (?, ?)",
            (doc_id, coll2_id),
        )
        
    client = TestClient(app)
    resp = client.delete(f"/collections/{coll1_id}")
    assert resp.status_code == 204
    
    with get_connection() as conn:
        # Collection 1 is deleted
        assert conn.execute("SELECT * FROM collections WHERE id = ?", (coll1_id,)).fetchone() is None
        # Collection 2 is preserved
        assert conn.execute("SELECT * FROM collections WHERE id = ?", (coll2_id,)).fetchone() is not None
        # Shared document is preserved
        assert conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone() is not None
        
    # Verify collection 1 vectors deleted but document vectors not deleted
    mock_store_instance.delete_by_collection.assert_called_once_with(coll1_id)
    mock_store_instance.delete_by_document.assert_not_called()



