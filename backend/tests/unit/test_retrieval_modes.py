import tempfile
import unittest
from pathlib import Path

from backend.app import create_app
from backend.services.retrieval_service import RetrievalService


class RetrievalModesUnitTests(unittest.TestCase):
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
        self.service = RetrievalService(
            sqlite_path=self.app.config["SQLITE_PATH"],
            chroma_client=self.app.extensions["chroma_client"],
            collection_prefix=self.app.config["CHROMA_COLLECTION_PREFIX"],
            embedding_model=self.app.config["DEFAULT_EMBEDDING_MODEL"],
            embedding_dimensions=self.app.config["EMBEDDING_DIMENSIONS"],
        )

    def tearDown(self):
        self.tempdir.cleanup()

    def test_empty_query_keyword_mode_returns_no_results(self):
        result = self.service.retrieve_keyword("", collection_id=None)
        self.assertEqual(result["retrieved_chunks"], [])
        self.assertEqual(result["metadata"]["rank_count"], 0)

    def test_dispatch_returns_correct_mode_label(self):
        semantic = self.service.retrieve("question", retrieval_mode="semantic")
        keyword = self.service.retrieve("question", retrieval_mode="keyword")
        hybrid = self.service.retrieve("question", retrieval_mode="hybrid")
        self.assertEqual(semantic["metadata"]["retrieval_mode_used"], "semantic")
        self.assertEqual(keyword["metadata"]["retrieval_mode_used"], "keyword")
        self.assertEqual(hybrid["metadata"]["retrieval_mode_used"], "hybrid")


if __name__ == "__main__":
    unittest.main()
