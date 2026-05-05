import io
import json
import tempfile
import unittest
from pathlib import Path

from backend.app import create_app


class CitationConsistencyIntegrationTests(unittest.TestCase):
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
        response = self.client.post(
            "/api/documents/upload",
            data={
                "collection_id": self.collection["collection_id"],
                "file": (io.BytesIO(b"Expense policy requires manager approval for reimbursements."), "expense.txt"),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        self.session = self.client.post(
            "/api/chat/sessions",
            json={
                "collection_id": self.collection["collection_id"],
                "retrieval_mode": "keyword",
            },
        ).get_json()

    def tearDown(self):
        self.tempdir.cleanup()

    def test_streamed_and_non_streamed_paths_match_final_citation_metadata(self):
        question = "What does the expense policy require for reimbursements?"

        non_stream = self.client.post(
            f"/api/chat/sessions/{self.session['session_id']}/ask",
            json={"question": question},
        ).get_json()

        stream_response = self.client.post(
            f"/api/chat/sessions/{self.session['session_id']}/ask-stream",
            json={"question": question},
            buffered=False,
        )
        events = [json.loads(line.decode("utf-8")) for line in stream_response.response if line.strip()]
        stream_completed = next(event for event in events if event["event"] == "completed")

        self.assertEqual(non_stream["answer"]["text"], stream_completed["answer"]["text"])
        self.assertEqual(
            [citation["chunk_id"] for citation in non_stream["citations"]],
            [citation["chunk_id"] for citation in stream_completed["citations"]],
        )
        self.assertEqual(
            [citation["document_id"] for citation in non_stream["citations"]],
            [citation["document_id"] for citation in stream_completed["citations"]],
        )


if __name__ == "__main__":
    unittest.main()
