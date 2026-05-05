import io
import tempfile
import unittest
from pathlib import Path

from backend.app import create_app
from backend.persistence.db import get_connection


class ChatFoundationIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        base_dir = Path(self.tempdir.name)
        self.app = create_app(
            {
                "TESTING": True,
                "DATA_DIR": str(base_dir / "data"),
                "UPLOAD_DIR": str(base_dir / "data" / "uploads"),
                "SQLITE_PATH": str(base_dir / "data" / "app.sqlite3"),
                "CHROMA_DIR": str(base_dir / "data" / "chroma"),
                "CHAT_RETRIEVAL_TOP_K": 5,
            }
        )
        self.client = self.app.test_client()
        self.collection = self.client.post("/api/collections", json={"name": "Policies"}).get_json()
        self._upload_text(
            "policy.txt",
            b"Vacation policy employees receive fifteen days of annual leave and ten sick days.",
            collection_id=self.collection["collection_id"],
        )
        self._upload_text(
            "security.txt",
            b"Security policy requires all employees to rotate passwords every ninety days.",
            collection_id=self.collection["collection_id"],
        )

    def tearDown(self):
        self.tempdir.cleanup()

    def _upload_text(self, filename, body, collection_id=None):
        response = self.client.post(
            "/api/documents/upload",
            data={
                "collection_id": collection_id or "",
                "file": (io.BytesIO(body), filename),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "completed")
        return response.get_json()

    def test_chat_schema_tables_exist(self):
        with get_connection(self.app.config["SQLITE_PATH"]) as connection:
            rows = connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        table_names = {row["name"] for row in rows}
        self.assertTrue(
            {
                "chat_sessions",
                "chat_messages",
                "turn_metadata",
                "refusal_logs",
                "citation_references",
                "chat_turn_logs",
            }.issubset(table_names)
        )

    def test_session_crud_and_history(self):
        create = self.client.post(
            "/api/chat/sessions",
            json={
                "collection_id": self.collection["collection_id"],
                "retrieval_mode": "semantic",
            },
        )
        self.assertEqual(create.status_code, 201)
        session = create.get_json()

        listing = self.client.get("/api/chat/sessions")
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(len(listing.get_json()["items"]), 1)

        history = self.client.get(f"/api/chat/sessions/{session['session_id']}")
        self.assertEqual(history.status_code, 200)
        payload = history.get_json()
        self.assertEqual(payload["session_id"], session["session_id"])
        self.assertEqual(payload["collection_id"], self.collection["collection_id"])
        self.assertEqual(payload["turns"], [])

    def test_retrieval_modes_return_consistent_metadata(self):
        session = self.client.post(
            "/api/chat/sessions",
            json={
                "collection_id": self.collection["collection_id"],
                "retrieval_mode": "semantic",
            },
        ).get_json()

        modes = ["semantic", "keyword", "hybrid"]
        results = {}
        for mode in modes:
            response = self.client.post(
                f"/api/chat/sessions/{session['session_id']}/ask",
                json={
                    "question": "What does the vacation policy say about annual leave?",
                    "retrieval_mode": mode,
                },
            )
            self.assertEqual(response.status_code, 200)
            payload = response.get_json()
            results[mode] = payload
            self.assertEqual(payload["retrieval_metadata"]["retrieval_mode_used"], mode)
            self.assertEqual(payload["result_type"], "answer")
            self.assertTrue(payload["citations"])
            citation = payload["citations"][0]
            self.assertIn("chunk_id", citation)
            self.assertIn("document_id", citation)
            self.assertIn("content_snippet", citation)

        self.assertIn("annual leave", results["keyword"]["answer"]["text"].lower())


if __name__ == "__main__":
    unittest.main()
