import io
import json
import tempfile
import unittest
from pathlib import Path

from backend.app import create_app


class CancellationIntegrationTests(unittest.TestCase):
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
            }
        )
        self.client = self.app.test_client()
        self.collection = self.client.post("/api/collections", json={"name": "Manual"}).get_json()
        self.client.post(
            "/api/documents/upload",
            data={
                "collection_id": self.collection["collection_id"],
                "file": (io.BytesIO(b"Support guide explains how to reset a password and unlock an account."), "support.txt"),
            },
            content_type="multipart/form-data",
        )
        self.session = self.client.post(
            "/api/chat/sessions",
            json={
                "collection_id": self.collection["collection_id"],
                "retrieval_mode": "keyword",
            },
        ).get_json()

    def tearDown(self):
        self.tempdir.cleanup()

    def test_cancellation_prevents_completed_citation_event(self):
        response = self.client.post(
            f"/api/chat/sessions/{self.session['session_id']}/ask-stream",
            json={"question": "How do I reset a password?"},
            buffered=False,
        )
        events = []
        turn_id = None
        for raw_line in response.response:
            line = raw_line.decode("utf-8").strip()
            if not line:
                continue
            event = json.loads(line)
            events.append(event)
            if event["event"] == "turn_created":
                turn_id = event["turn_id"]
                cancel = self.client.post(
                    f"/api/chat/sessions/{self.session['session_id']}/turns/{turn_id}/cancel"
                )
                self.assertEqual(cancel.status_code, 200)
        self.assertIsNotNone(turn_id)
        event_names = [event["event"] for event in events]
        self.assertIn("cancelled", event_names)
        self.assertNotIn(
            {"event": "completed", "turn_id": turn_id},
            events,
        )


if __name__ == "__main__":
    unittest.main()
