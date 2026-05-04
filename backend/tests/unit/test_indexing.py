import tempfile
import unittest
from pathlib import Path

from backend.persistence.chroma import init_chroma_client
from backend.services.indexing_service import IndexingService


class IndexingTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.chroma_dir = Path(self.tempdir.name) / "chroma"
        self.client = init_chroma_client(self.chroma_dir)
        self.service = IndexingService(self.client, collection_prefix="test", dimensions=8)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_index_chunks_stores_metadata_and_embeddings(self):
        document = {"document_id": "doc_1", "collection_id": "col_a"}
        chunks = [
            {
                "chunk_id": "chunk_1",
                "document_id": "doc_1",
                "collection_id": "col_a",
                "source_type": "text",
                "title": "Fixture",
                "source_url": "",
                "section_name": "Intro",
                "page_number": None,
                "chunk_order": 1,
                "chunk_text": "Alpha beta gamma",
                "content_hash": "hash_1",
            }
        ]

        result = self.service.index_chunks(document, chunks)
        stored = self.client.get_collection("test_col_a").get(ids=["chunk_1"], include=["embeddings", "metadatas", "documents"])

        self.assertEqual(result["chunk_count"], 1)
        self.assertEqual(len(stored["embeddings"][0]), 8)
        self.assertEqual(stored["metadatas"][0]["document_id"], "doc_1")
        self.assertEqual(stored["metadatas"][0]["section_name"], "Intro")
        self.assertEqual(stored["documents"][0], "Alpha beta gamma")

    def test_move_document_reindexes_into_new_collection_namespace(self):
        document = {"document_id": "doc_2", "collection_id": "col_a"}
        chunks = [
            {
                "chunk_id": "chunk_2",
                "document_id": "doc_2",
                "collection_id": "col_a",
                "source_type": "text",
                "title": "Fixture",
                "source_url": "",
                "section_name": "",
                "page_number": None,
                "chunk_order": 1,
                "chunk_text": "Move me",
                "content_hash": "hash_2",
            }
        ]

        self.service.index_chunks(document, chunks)
        self.service.move_document(document, chunks, "col_b")

        old_collection = self.client.get_collection("test_col_a").get(where={"document_id": "doc_2"})
        new_collection = self.client.get_collection("test_col_b").get(where={"document_id": "doc_2"})

        self.assertEqual(old_collection["ids"], [])
        self.assertEqual(new_collection["ids"], ["chunk_2"])
        self.assertEqual(new_collection["metadatas"][0]["collection_id"], "col_b")

    def test_delete_document_removes_vectors(self):
        document = {"document_id": "doc_3", "collection_id": "col_a"}
        chunks = [
            {
                "chunk_id": "chunk_3",
                "document_id": "doc_3",
                "collection_id": "col_a",
                "source_type": "text",
                "title": "Fixture",
                "source_url": "",
                "section_name": "",
                "page_number": None,
                "chunk_order": 1,
                "chunk_text": "Delete me",
                "content_hash": "hash_3",
            }
        ]

        self.service.index_chunks(document, chunks)
        self.service.delete_document(document)
        stored = self.client.get_collection("test_col_a").get(where={"document_id": "doc_3"})

        self.assertEqual(stored["ids"], [])


if __name__ == "__main__":
    unittest.main()
