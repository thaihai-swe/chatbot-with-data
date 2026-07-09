"""Tests for database migrations."""

from __future__ import annotations

import pytest
from database import get_connection
from migrations.runner import apply_migrations, reset_database


@pytest.fixture
def fresh_db():
    """Create a fresh database with all migrations applied."""
    reset_database()
    apply_migrations()
    yield
    reset_database()
    apply_migrations()


def test_provenance_column(fresh_db):
    """Migration 0007 adds provenance_json; default '{}'; round-trip works; idempotent."""
    import json

    with get_connection() as conn:
        columns = [row[1] for row in conn.execute("PRAGMA table_info(chat_turns)")]
        assert "provenance_json" in columns

        conn.execute("INSERT INTO chat_sessions (id) VALUES (?)", ("sess-prov",))
        conn.execute(
            "INSERT INTO chat_turns (id, session_id, query_text) VALUES (?, ?, ?)",
            ("turn-prov", "sess-prov", "q"),
        )
        default = conn.execute(
            "SELECT provenance_json FROM chat_turns WHERE id = ?", ("turn-prov",)
        ).fetchone()[0]
        assert default == "{}"

        payload = {"claims": [], "coverage": {"cited": 0, "total": 0, "uncited_indices": []}}
        conn.execute(
            "UPDATE chat_turns SET provenance_json = ? WHERE id = ?",
            (json.dumps(payload), "turn-prov"),
        )
        stored = conn.execute(
            "SELECT provenance_json FROM chat_turns WHERE id = ?", ("turn-prov",)
        ).fetchone()[0]
        assert json.loads(stored) == payload

    apply_migrations()
    with get_connection() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM schema_migrations WHERE version = ?",
            ("0007_provenance_json",),
        ).fetchone()[0]
    assert count == 1


class TestMigrations:
    def test_0007_provenance_column_exists(self, fresh_db):
        """Migration 0007 adds provenance_json column to chat_turns."""
        with get_connection() as conn:
            cursor = conn.execute("PRAGMA table_info(chat_turns)")
            columns = [row[1] for row in cursor.fetchall()]

        assert "provenance_json" in columns

    def test_0007_provenance_column_defaults_to_empty_object(self, fresh_db):
        """New turns have provenance_json defaulting to '{}'."""
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO chat_sessions (id) VALUES (?)",
                ("test-session",),
            )
            conn.execute(
                "INSERT INTO chat_turns (id, session_id, query_text) VALUES (?, ?, ?)",
                ("turn-1", "test-session", "test query"),
            )
            cursor = conn.execute(
                "SELECT provenance_json FROM chat_turns WHERE id = ?",
                ("turn-1",),
            )
            row = cursor.fetchone()

        assert row[0] == "{}"

    def test_0007_migration_is_idempotent(self, fresh_db):
        """Running 0007 migration twice does not error."""
        # Apply again - should not raise
        apply_migrations()

        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM schema_migrations WHERE version = ?",
                ("0007_provenance_json",),
            )
            count = cursor.fetchone()[0]

        assert count == 1

    def test_0007_provenance_column_roundtrip(self, fresh_db):
        """Can write and read provenance_json value."""
        import json

        provenance_data = {
            "claims": [
                {"index": 0, "text": "Claim 1", "cited": True, "chunks": ["chunk-1"]},
                {"index": 1, "text": "Claim 2", "cited": False, "chunks": []},
            ],
            "coverage": {"cited": 1, "total": 2, "uncited_indices": [1]},
        }
        provenance_json = json.dumps(provenance_data)

        with get_connection() as conn:
            conn.execute(
                "INSERT INTO chat_sessions (id) VALUES (?)",
                ("test-session-2",),
            )
            conn.execute(
                "INSERT INTO chat_turns (id, session_id, query_text, provenance_json) VALUES (?, ?, ?, ?)",
                ("turn-2", "test-session-2", "test query", provenance_json),
            )
            cursor = conn.execute(
                "SELECT provenance_json FROM chat_turns WHERE id = ?",
                ("turn-2",),
            )
            row = cursor.fetchone()

        assert json.loads(row[0]) == provenance_data