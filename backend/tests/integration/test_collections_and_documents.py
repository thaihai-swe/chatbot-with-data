import tempfile
import unittest
from pathlib import Path

from backend.app import create_app


class CollectionsAndDocumentsIntegrationTest(unittest.TestCase):
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

    def test_collection_crud_and_document_move_flow(self):
        create_first = self.client.post(
            "/api/collections",
            json={"name": "Product Docs", "description": "Primary docs"},
        )
        self.assertEqual(create_first.status_code, 201)
        first_collection = create_first.get_json()

        create_second = self.client.post(
            "/api/collections",
            json={"name": "Research Papers", "description": "Notes"},
        )
        self.assertEqual(create_second.status_code, 201)
        second_collection = create_second.get_json()

        set_default = self.client.patch(
            f"/api/collections/{first_collection['collection_id']}/default"
        )
        self.assertEqual(set_default.status_code, 200)
        self.assertEqual(set_default.get_json()["is_default"], 1)

        create_document = self.client.post(
            "/api/documents",
            json={
                "source_type": "text",
                "collection_id": first_collection["collection_id"],
                "title": "Architecture Overview",
                "raw_text": "System architecture details",
                "ingestion_status": "completed",
            },
        )
        self.assertEqual(create_document.status_code, 201)
        document = create_document.get_json()
        self.assertEqual(document["collection_id"], first_collection["collection_id"])

        move_document = self.client.patch(
            f"/api/documents/{document['document_id']}/collection",
            json={"collection_id": second_collection["collection_id"]},
        )
        self.assertEqual(move_document.status_code, 200)
        moved = move_document.get_json()
        self.assertEqual(moved["collection_id"], second_collection["collection_id"])

        documents_in_second = self.client.get(
            "/api/documents", query_string={"collection_id": second_collection["collection_id"]}
        )
        self.assertEqual(documents_in_second.status_code, 200)
        items = documents_in_second.get_json()["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["document_id"], document["document_id"])

        delete_non_empty = self.client.delete(
            f"/api/collections/{second_collection['collection_id']}"
        )
        self.assertEqual(delete_non_empty.status_code, 400)

        delete_document = self.client.delete(f"/api/documents/{document['document_id']}")
        self.assertEqual(delete_document.status_code, 200)

        delete_collection = self.client.delete(
            f"/api/collections/{second_collection['collection_id']}"
        )
        self.assertEqual(delete_collection.status_code, 200)


if __name__ == "__main__":
    unittest.main()
