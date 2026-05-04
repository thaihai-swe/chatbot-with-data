import io
import tempfile
import unittest
from pathlib import Path

from backend.app import create_app


class ObservabilityLogTests(unittest.TestCase):
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

    def tearDown(self):
        self.tempdir.cleanup()

    def test_ingestion_logs_capture_duplicate_detection_and_user_decision(self):
        first = self.client.post(
            "/api/documents/upload",
            data={"file": (io.BytesIO(b"Repeat me"), "repeat.txt")},
            content_type="multipart/form-data",
        )
        self.assertEqual(first.status_code, 200)
        original_document_id = first.get_json()["document_id"]

        duplicate = self.client.post(
            "/api/documents/upload",
            data={"file": (io.BytesIO(b"Repeat me"), "repeat-copy.txt")},
            content_type="multipart/form-data",
        )
        self.assertEqual(duplicate.status_code, 200)
        duplicate_payload = duplicate.get_json()
        self.assertEqual(duplicate_payload["status"], "duplicate_detected")

        decision = self.client.patch(
            f"/api/documents/{duplicate_payload['document_id']}/duplicate-decision",
            json={"decision": "skip"},
        )
        self.assertEqual(decision.status_code, 200)

        logs = self.client.get("/api/ingestion-logs")
        self.assertEqual(logs.status_code, 200)
        items = logs.get_json()["items"]
        self.assertGreaterEqual(len(items), 2)

        duplicate_log = next(item for item in items if item["document_id"] == duplicate_payload["document_id"])
        unique_log = next(item for item in items if item["document_id"] == original_document_id)

        self.assertEqual(duplicate_log["status"], "skipped")
        self.assertEqual(duplicate_log["duplicate_class"], duplicate_payload["duplicate_class"])
        self.assertEqual(duplicate_log["matched_document_id"], original_document_id)
        self.assertEqual(duplicate_log["user_decision"], "skip")
        self.assertIsNotNone(duplicate_log["detection_method"])
        self.assertTrue(duplicate_log["created_at"])

        self.assertEqual(unique_log["status"], "completed")
        self.assertEqual(unique_log["source_type"], "text")
        self.assertTrue(unique_log["source_identifier"])


if __name__ == "__main__":
    unittest.main()
