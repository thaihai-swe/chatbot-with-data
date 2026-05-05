import io
import tempfile
import unittest
from pathlib import Path

from backend.app import create_app


class Feature2RegressionIntegrationTests(unittest.TestCase):
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
        self.collection = self.client.post("/api/collections", json={"name": "Handbook"}).get_json()
        self.client.post(
            "/api/documents/upload",
            data={
                "collection_id": self.collection["collection_id"],
                "file": (io.BytesIO(b"Benefits handbook says employees receive fifteen days of annual leave and ten sick days."), "benefits.txt"),
            },
            content_type="multipart/form-data",
        )

    def tearDown(self):
        self.tempdir.cleanup()

    def _session(self):
        response = self.client.post(
            "/api/chat/sessions",
            json={"collection_id": self.collection["collection_id"], "retrieval_mode": "keyword"},
        )
        return response.get_json()

    def test_benign_supported_question_still_answers_without_warning(self):
        session = self._session()
        response = self.client.post(
            f"/api/chat/sessions/{session['session_id']}/ask",
            json={"question": "How many sick days do employees receive?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["result_type"], "answer")
        self.assertEqual(payload["prompt_injection_result"], "clear")
        self.assertEqual(payload["safety_issue_count"], 0)
        self.assertTrue(payload["citations"])


if __name__ == "__main__":
    unittest.main()
