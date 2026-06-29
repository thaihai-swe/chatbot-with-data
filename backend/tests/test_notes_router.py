from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from database import get_connection
from app import app


@pytest.fixture(autouse=True)
def seed_data():
    chunk_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    coll_id = str(uuid.uuid4())
    with get_connection() as conn:
        conn.execute("INSERT INTO collections (id, name) VALUES (?, ?)", (coll_id, f"test-coll-{coll_id}"))
        conn.execute(
            "INSERT INTO documents (id, title, source_type, extracted_text) VALUES (?, ?, ?, ?)",
            (doc_id, "Test Doc", "manual", "test text"),
        )
        conn.execute(
            "INSERT INTO chunks (id, document_id, collection_id, chunk_order, strategy, source_type, text, text_length) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (chunk_id, doc_id, coll_id, 0, "test", "manual", "test", 4),
        )
    return {"chunk_id": chunk_id}


client = TestClient(app)


class TestNotesRouter:
    def test_get_note_returns_none_when_not_found(self, seed_data):
        resp = client.get(f"/chunks/{seed_data['chunk_id']}/notes")
        assert resp.status_code == 200
        assert resp.json() is None

    def test_put_creates_note(self, seed_data):
        chunk_id = seed_data["chunk_id"]
        resp = client.put(f"/chunks/{chunk_id}/notes", json={"note_text": "test annotation"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["chunk_id"] == chunk_id
        assert data["note_text"] == "test annotation"

    def test_get_returns_saved_note(self, seed_data):
        chunk_id = seed_data["chunk_id"]
        client.put(f"/chunks/{chunk_id}/notes", json={"note_text": "persistent note"})
        resp = client.get(f"/chunks/{chunk_id}/notes")
        assert resp.status_code == 200
        assert resp.json()["note_text"] == "persistent note"

    def test_put_updates_existing_note(self, seed_data):
        chunk_id = seed_data["chunk_id"]
        client.put(f"/chunks/{chunk_id}/notes", json={"note_text": "original"})
        resp = client.put(f"/chunks/{chunk_id}/notes", json={"note_text": "updated"})
        assert resp.status_code == 200
        assert resp.json()["note_text"] == "updated"

    def test_rejects_note_over_2000_chars(self, seed_data):
        resp = client.put(
            f"/chunks/{seed_data['chunk_id']}/notes",
            json={"note_text": "x" * 2001},
        )
        assert resp.status_code == 422

    def test_returns_404_for_nonexistent_chunk(self):
        resp = client.put("/chunks/nonexistent/notes", json={"note_text": "test"})
        assert resp.status_code == 404
