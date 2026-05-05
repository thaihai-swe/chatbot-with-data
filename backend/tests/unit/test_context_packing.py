import unittest

from backend.services.context_packing_service import ContextPackingService


class ContextPackingUnitTests(unittest.TestCase):
    def setUp(self):
        self.service = ContextPackingService(token_budget=8)

    def test_selects_highest_ranked_chunks_within_budget(self):
        packed = self.service.pack(
            [
                {"chunk_id": "a", "retrieval_score": 0.9, "full_text": "one two three"},
                {"chunk_id": "b", "retrieval_score": 0.8, "full_text": "four five six seven"},
                {"chunk_id": "c", "retrieval_score": 0.7, "full_text": "eight nine ten eleven"},
            ]
        )
        self.assertEqual([chunk["chunk_id"] for chunk in packed["selected_chunks"]], ["a", "b"])
        self.assertLessEqual(packed["total_tokens"], 8)


if __name__ == "__main__":
    unittest.main()
