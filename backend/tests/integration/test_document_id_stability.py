import io
import tempfile
import unittest
from pathlib import Path

from backend.app import create_app


class DocumentIdStabilityTests(unittest.TestCase):
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

    def _create_collection(self, name="Stable IDs"):
        response = self.client.post("/api/collections", json={"name": name})
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def test_document_id_stays_stable_through_duplicate_handling_move_and_reindex(self):
        collection = self._create_collection("Primary")
        backup = self._create_collection("Backup")

        first = self.client.post(
            "/api/documents/upload",
            data={
                "collection_id": collection["collection_id"],
                "file": (io.BytesIO(b"Stable identity content"), "stable.txt"),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(first.status_code, 200)
        original_document_id = first.get_json()["document_id"]

        duplicate = self.client.post(
            "/api/documents/upload",
            data={
                "collection_id": collection["collection_id"],
                "file": (io.BytesIO(b"Stable identity content"), "stable-copy.txt"),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(duplicate.status_code, 200)
        duplicate_payload = duplicate.get_json()
        self.assertEqual(duplicate_payload["matched_document_id"], original_document_id)

        replace = self.client.patch(
            f"/api/documents/{duplicate_payload['document_id']}/duplicate-decision",
            json={"decision": "replace"},
        )
        self.assertEqual(replace.status_code, 200)
        self.assertEqual(replace.get_json()["document_id"], original_document_id)

        move = self.client.patch(
            f"/api/documents/{original_document_id}/collection",
            json={"collection_id": backup["collection_id"]},
        )
        self.assertEqual(move.status_code, 200)
        self.assertEqual(move.get_json()["document_id"], original_document_id)

        reindex = self.client.post(f"/api/documents/{original_document_id}/re-index")
        self.assertEqual(reindex.status_code, 200)
        self.assertEqual(reindex.get_json()["document_id"], original_document_id)


if __name__ == "__main__":
    unittest.main()
