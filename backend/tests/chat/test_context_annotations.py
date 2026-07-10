from __future__ import annotations

import uuid

import pytest

from chat.context import ContextService, load_chunk_notes
from database import get_connection


@pytest.fixture
def seed_chunks():
    chunk_ids = []
    with get_connection() as conn:
        for i in range(3):
            cid = str(uuid.uuid4())
            did = str(uuid.uuid4())
            coll_id = str(uuid.uuid4())
            conn.execute("INSERT INTO collections (id, name) VALUES (?, ?)", (coll_id, f"test-coll-{coll_id}"))
            conn.execute(
                "INSERT INTO documents (id, title, source_type, extracted_text) VALUES (?, ?, ?, ?)",
                (did, f"Doc {i}", "manual", f"text {i}"),
            )
            conn.execute(
                "INSERT INTO chunks (id, document_id, collection_id, chunk_order, strategy, source_type, text, text_length) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (cid, did, coll_id, i, "test", "manual", f"Chunk {i} content", 15),
            )
            chunk_ids.append(cid)

    # Add notes for first two chunks
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO chunk_notes (chunk_id, note_text) VALUES (?, ?)",
            (chunk_ids[0], "Pay attention to dates"),
        )
        conn.execute(
            "INSERT INTO chunk_notes (chunk_id, note_text) VALUES (?, ?)",
            (chunk_ids[1], "Verify this claim"),
        )

    return chunk_ids


class TestLoadChunkNotes:
    def test_returns_notes_for_existing_chunks(self, seed_chunks):
        notes = load_chunk_notes(seed_chunks[:2])
        assert len(notes) == 2
        assert notes[seed_chunks[0]] == "Pay attention to dates"
        assert notes[seed_chunks[1]] == "Verify this claim"

    def test_skips_missing_chunks(self, seed_chunks):
        notes = load_chunk_notes([str(uuid.uuid4())])
        assert notes == {}

    def test_returns_empty_for_empty_input(self, seed_chunks):
        assert load_chunk_notes([]) == {}


class TestContextAnnotationInjection:
    def test_injects_user_note_in_source_tag(self, seed_chunks):
        chunks = [
            {"chunk_id": seed_chunks[0], "title": "Doc A", "text": "Content A", "document_id": "d1"},
            {"chunk_id": seed_chunks[1], "title": "Doc B", "text": "Content B", "document_id": "d2"},
            {"chunk_id": seed_chunks[2], "title": "Doc C", "text": "Content C", "document_id": "d3"},
        ]
        annotations = load_chunk_notes(seed_chunks)
        svc = ContextService()
        result = svc.assemble_context("test query", chunks, [], annotations=annotations)
        context = result["context_string"]

        # Chunks 0 and 1 have notes, chunk 2 does not
        assert 'Note: Pay attention to dates' in context
        assert 'Note: Verify this claim' in context
        assert context.count("Note:") == 2  # Only 2 out of 3 chunks have notes

    def test_no_user_note_when_no_annotations(self, seed_chunks):
        chunks = [
            {"chunk_id": seed_chunks[0], "title": "Doc A", "text": "Content A", "document_id": "d1"},
        ]
        svc = ContextService()
        result = svc.assemble_context("test query", chunks, [])
        context = result["context_string"]
        assert "Note:" not in context

    def test_notes_query_sub_10ms(self, seed_chunks):
        import time
        start = time.perf_counter()
        load_chunk_notes(seed_chunks)
        elapsed = (time.perf_counter() - start) * 1000
        assert elapsed < 10, f"Notes query took {elapsed:.2f}ms (expected <10ms)"
