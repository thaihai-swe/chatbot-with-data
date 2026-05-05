import io
import tempfile
import unittest
from pathlib import Path

from backend.app import create_app


class RefusalCorrectnessIntegrationTests(unittest.TestCase):
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
                "ANSWERABILITY_MIN_SIMILARITY": 0.95,
            }
        )
        self.client = self.app.test_client()
        self.collection = self.client.post("/api/collections", json={"name": "Policies"}).get_json()
        self._upload("alpha.txt", b"Vacation policy says annual leave is fifteen days.")
        self._upload("beta.txt", b"Retention policy says records are stored for seven years.")
        self.session = self.client.post(
            "/api/chat/sessions",
            json={"collection_id": self.collection["collection_id"], "retrieval_mode": "semantic"},
        ).get_json()

    def tearDown(self):
        self.tempdir.cleanup()

    def _upload(self, filename, body):
        response = self.client.post(
            "/api/documents/upload",
            data={
                "collection_id": self.collection["collection_id"],
                "file": (io.BytesIO(body), filename),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        if payload["status"] == "duplicate_detected":
            decision = self.client.patch(
                f"/api/documents/{payload['document_id']}/duplicate-decision",
                json={"decision": "ingest-anyway"},
            )
            self.assertEqual(decision.status_code, 200)

    def test_low_confidence_refusal(self):
        response = self.client.post(
            f"/api/chat/sessions/{self.session['session_id']}/ask",
            json={"question": "Tell me about annual leave"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["result_type"], "refusal")
        self.assertEqual(payload["refusal"]["reason_category"], "low_confidence")
        self.assertNotIn("error", payload["refusal"]["refusal_text"].lower())

    def test_conflicting_evidence_refusal(self):
        self._upload("conflict-one.txt", b"Retention policy says records are stored for seven years.")
        self._upload("conflict-two.txt", b"Retention policy says records are stored for five years.")
        session = self.client.post(
            "/api/chat/sessions",
            json={"collection_id": self.collection["collection_id"], "retrieval_mode": "keyword"},
        ).get_json()
        response = self.client.post(
            f"/api/chat/sessions/{session['session_id']}/ask",
            json={"question": "How many years are records stored?"},
        )
        payload = response.get_json()
        self.assertEqual(payload["result_type"], "refusal")
        self.assertEqual(payload["refusal"]["reason_category"], "conflicting_evidence")


if __name__ == "__main__":
    unittest.main()
