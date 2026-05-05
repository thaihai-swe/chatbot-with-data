import unittest

from backend.services.answerability_service import AnswerabilityService


class AnswerabilityUnitTests(unittest.TestCase):
    def setUp(self):
        self.service = AnswerabilityService(
            min_similarity_threshold=0.5,
            min_chunk_count=1,
            min_query_overlap=0.2,
            consistency_threshold=0.8,
        )

    def test_no_relevant_evidence(self):
        result = self.service.evaluate("question", [])
        self.assertFalse(result["answerable"])
        self.assertEqual(result["reason_category"], "no_relevant_evidence")

    def test_low_confidence(self):
        result = self.service.evaluate(
            "question",
            [{"retrieval_score": 0.3, "query_overlap": 0.5, "full_text": "alpha"}],
        )
        self.assertEqual(result["reason_category"], "low_confidence")

    def test_out_of_domain(self):
        result = self.service.evaluate(
            "question",
            [{"retrieval_score": 0.8, "query_overlap": 0.0, "full_text": "alpha"}],
        )
        self.assertEqual(result["reason_category"], "out_of_domain")

    def test_conflicting_evidence(self):
        result = self.service.evaluate(
            "How many years are records stored?",
            [
                {"retrieval_score": 0.9, "query_overlap": 0.8, "full_text": "Records are stored for 5 years."},
                {"retrieval_score": 0.88, "query_overlap": 0.8, "full_text": "Records are stored for 7 years."},
            ],
        )
        self.assertEqual(result["reason_category"], "conflicting_evidence")


if __name__ == "__main__":
    unittest.main()
