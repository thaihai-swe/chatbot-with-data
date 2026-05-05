import io
import json
import tempfile
import unittest
from pathlib import Path

from backend.app import create_app


class ChatOrchestrationIntegrationTests(unittest.TestCase):
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
        self._upload(
            "benefits.txt",
            b"Benefits handbook says employees receive fifteen days of annual leave and ten sick days.",
        )
        self._upload(
            "travel.txt",
            b"Travel handbook says receipts are required for reimbursement and managers approve flights.",
        )

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

    def _session(self, retrieval_mode="keyword"):
        response = self.client.post(
            "/api/chat/sessions",
            json={
                "collection_id": self.collection["collection_id"],
                "retrieval_mode": retrieval_mode,
            },
        )
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def test_supported_question_returns_grounded_answer_and_citations(self):
        session = self._session("keyword")
        response = self.client.post(
            f"/api/chat/sessions/{session['session_id']}/ask",
            json={"question": "How many days of annual leave do employees receive?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["result_type"], "answer")
        self.assertIn("annual leave", payload["answer"]["text"].lower())
        self.assertTrue(payload["citations"])
        self.assertEqual(payload["terminal_status"], "completed")

    def test_no_evidence_question_returns_refusal(self):
        session = self._session("keyword")
        response = self.client.post(
            f"/api/chat/sessions/{session['session_id']}/ask",
            json={"question": "What is the cafeteria lunch menu?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["result_type"], "refusal")
        self.assertEqual(payload["refusal"]["reason_category"], "no_relevant_evidence")
        self.assertEqual(payload["terminal_status"], "refused")

    def test_streaming_returns_events_and_final_citations(self):
        session = self._session("keyword")
        response = self.client.post(
            f"/api/chat/sessions/{session['session_id']}/ask-stream",
            json={"question": "How many sick days do employees receive?"},
            buffered=False,
        )
        self.assertEqual(response.status_code, 200)
        events = [json.loads(line.decode("utf-8")) for line in response.response if line.strip()]
        event_names = [event["event"] for event in events]
        self.assertIn("retrieving", event_names)
        self.assertIn("context_packed", event_names)
        self.assertIn("generating", event_names)
        self.assertIn("completed", event_names)
        completed = next(event for event in events if event["event"] == "completed")
        self.assertEqual(completed["result_type"], "answer")
        self.assertTrue(completed["citations"])

    def test_follow_up_question_uses_recent_history_for_retrieval(self):
        session = self._session("keyword")
        first = self.client.post(
            f"/api/chat/sessions/{session['session_id']}/ask",
            json={"question": "How many days of annual leave do employees receive?"},
        )
        self.assertEqual(first.status_code, 200)

        follow_up = self.client.post(
            f"/api/chat/sessions/{session['session_id']}/ask",
            json={"question": "How many is that?"},
        )
        self.assertEqual(follow_up.status_code, 200)
        payload = follow_up.get_json()
        self.assertEqual(payload["result_type"], "answer")
        self.assertIn("fifteen", payload["answer"]["text"].lower())
        self.assertTrue(payload["citations"])


if __name__ == "__main__":
    unittest.main()
