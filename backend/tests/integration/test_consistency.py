import io
import tempfile
import unittest
from pathlib import Path

from backend.app import create_app
from backend.persistence.db import get_connection


class ConsistencyIntegrationTests(unittest.TestCase):
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
                "DEFAULT_CHUNK_SIZE": 16,
                "DEFAULT_CHUNK_OVERLAP": 4,
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.tempdir.cleanup()

    def _create_collection(self, name):
        response = self.client.post("/api/collections", json={"name": name})
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def _upload_text_document(self, collection_id, filename="notes.txt", body=b"Alpha beta gamma delta epsilon"):
        response = self.client.post(
            "/api/documents/upload",
            data={
                "collection_id": collection_id,
                "file": (io.BytesIO(body), filename),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "completed")
        return response.get_json()["document_id"]

    def test_move_updates_sqlite_and_chroma_collection_membership(self):
        source = self._create_collection("Source")
        target = self._create_collection("Target")
        document_id = self._upload_text_document(source["collection_id"])

        response = self.client.patch(
            f"/api/documents/{document_id}/collection",
            json={"collection_id": target["collection_id"]},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["collection_id"], target["collection_id"])

        with get_connection(self.app.config["SQLITE_PATH"]) as connection:
            chunks = connection.execute(
                "SELECT collection_id FROM chunk_metadata WHERE document_id = ?",
                (document_id,),
            ).fetchall()
        self.assertTrue(chunks)
        self.assertEqual({row["collection_id"] for row in chunks}, {target["collection_id"]})

        old_vectors = self.app.extensions["chroma_client"].get_collection(
            f"{self.app.config['CHROMA_COLLECTION_PREFIX']}_{source['collection_id']}"
        ).get(where={"document_id": document_id})
        new_vectors = self.app.extensions["chroma_client"].get_collection(
            f"{self.app.config['CHROMA_COLLECTION_PREFIX']}_{target['collection_id']}"
        ).get(where={"document_id": document_id})

        self.assertEqual(old_vectors["ids"], [])
        self.assertTrue(new_vectors["ids"])

    def test_delete_non_empty_collection_is_rejected_without_orphans(self):
        collection = self._create_collection("Protected")
        document_id = self._upload_text_document(collection["collection_id"])

        response = self.client.delete(f"/api/collections/{collection['collection_id']}")
        self.assertEqual(response.status_code, 400)
        self.assertIn("must be empty", response.get_json()["error"])

        document = self.client.get(f"/api/documents/{document_id}")
        self.assertEqual(document.status_code, 200)

    def test_delete_document_removes_sqlite_chunks_and_chroma_vectors(self):
        collection = self._create_collection("Delete Test")
        document_id = self._upload_text_document(collection["collection_id"])

        delete = self.client.delete(f"/api/documents/{document_id}")
        self.assertEqual(delete.status_code, 200)

        with get_connection(self.app.config["SQLITE_PATH"]) as connection:
            document_row = connection.execute(
                "SELECT document_id FROM documents WHERE document_id = ?",
                (document_id,),
            ).fetchone()
            chunk_rows = connection.execute(
                "SELECT chunk_id FROM chunk_metadata WHERE document_id = ?",
                (document_id,),
            ).fetchall()
        self.assertIsNone(document_row)
        self.assertEqual(chunk_rows, [])

        vectors = self.app.extensions["chroma_client"].get_collection(
            f"{self.app.config['CHROMA_COLLECTION_PREFIX']}_{collection['collection_id']}"
        ).get(where={"document_id": document_id})
        self.assertEqual(vectors["ids"], [])


if __name__ == "__main__":
    unittest.main()
