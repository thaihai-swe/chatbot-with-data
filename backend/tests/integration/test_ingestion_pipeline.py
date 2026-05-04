import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.app import create_app


class IngestionPipelineIntegrationTest(unittest.TestCase):
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
                "DEFAULT_CHUNK_SIZE": 24,
                "DEFAULT_CHUNK_OVERLAP": 6,
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.tempdir.cleanup()

    def _create_collection(self, name="Docs"):
        response = self.client.post("/api/collections", json={"name": name})
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def test_upload_duplicate_decision_reindex_and_delete(self):
        collection = self._create_collection()

        upload = self.client.post(
            "/api/documents/upload",
            data={
                "collection_id": collection["collection_id"],
                "file": (io.BytesIO(b"Heading\nBody text for ingestion."), "notes.txt"),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(upload.status_code, 200)
        uploaded = upload.get_json()
        self.assertEqual(uploaded["status"], "completed")

        detail = self.client.get(f"/api/documents/{uploaded['document_id']}")
        self.assertEqual(detail.status_code, 200)
        detail_payload = detail.get_json()
        self.assertGreaterEqual(detail_payload["chunk_count"], 1)
        self.assertEqual(detail_payload["collection_id"], collection["collection_id"])

        duplicate = self.client.post(
            "/api/documents/upload",
            data={
                "collection_id": collection["collection_id"],
                "file": (io.BytesIO(b"Heading\nBody text for ingestion."), "notes-copy.txt"),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(duplicate.status_code, 200)
        duplicate_payload = duplicate.get_json()
        self.assertEqual(duplicate_payload["status"], "duplicate_detected")
        self.assertIn(
            duplicate_payload["duplicate_class"],
            {"exact_duplicate", "same_content_different_source"},
        )

        decide = self.client.patch(
            f"/api/documents/{duplicate_payload['document_id']}/duplicate-decision",
            json={"decision": "version-as-new"},
        )
        self.assertEqual(decide.status_code, 200)
        self.assertEqual(decide.get_json()["ingestion_status"], "completed")

        reindex = self.client.post(f"/api/documents/{uploaded['document_id']}/re-index")
        self.assertEqual(reindex.status_code, 200)
        self.assertEqual(reindex.get_json()["document_id"], uploaded["document_id"])

        logs = self.client.get("/api/ingestion-logs")
        self.assertEqual(logs.status_code, 200)
        self.assertGreaterEqual(len(logs.get_json()["items"]), 2)

        delete = self.client.delete(f"/api/documents/{uploaded['document_id']}")
        self.assertEqual(delete.status_code, 200)

        deleted_detail = self.client.get(f"/api/documents/{uploaded['document_id']}")
        self.assertEqual(deleted_detail.status_code, 404)

    @patch("backend.parsers.url_parser.requests.get")
    def test_url_ingestion_and_skip_duplicate(self, mock_get):
        mock_response = unittest.mock.Mock()
        mock_response.text = "<html><head><title>Docs</title></head><body>Alpha Beta Gamma</body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        first = self.client.post("/api/documents/ingest-url", json={"url": "https://example.com/docs"})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.get_json()["status"], "completed")

        duplicate = self.client.post("/api/documents/ingest-url", json={"url": "https://example.com/docs/"})
        self.assertEqual(duplicate.status_code, 200)
        self.assertEqual(duplicate.get_json()["status"], "duplicate_detected")

        skip = self.client.patch(
            f"/api/documents/{duplicate.get_json()['document_id']}/duplicate-decision",
            json={"decision": "skip"},
        )
        self.assertEqual(skip.status_code, 200)
        self.assertEqual(skip.get_json()["ingestion_status"], "skipped")


if __name__ == "__main__":
    unittest.main()
