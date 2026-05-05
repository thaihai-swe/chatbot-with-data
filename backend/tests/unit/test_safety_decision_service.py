import unittest

from backend.services.safety_decision_service import SafetyDecisionService


class SafetyDecisionServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = SafetyDecisionService()

    def test_user_query_high_risk_refuses(self):
        result = self.service.decide(
            [
                {
                    "issue_scope": "user_query",
                    "risk_score": 95,
                    "recommended_action": "refuse",
                }
            ]
        )
        self.assertEqual(result["overall_action"], "refuse")
        self.assertEqual(result["prompt_injection_result"], "refused")

    def test_medium_risk_chunk_is_excluded(self):
        result = self.service.decide(
            [
                {
                    "issue_scope": "retrieved_chunk",
                    "risk_score": 76,
                    "recommended_action": "exclude_chunk",
                    "affected_chunk_id": "chunk_1",
                }
            ]
        )
        self.assertEqual(result["overall_action"], "exclude_chunk")
        self.assertEqual(result["excluded_chunk_ids"], ["chunk_1"])

    def test_lower_trust_action_is_used_for_midrange_chunk_risk(self):
        result = self.service.decide(
            [
                {
                    "issue_scope": "retrieved_chunk",
                    "risk_score": 60,
                    "recommended_action": "lower_trust",
                    "affected_chunk_id": "chunk_2",
                }
            ]
        )
        self.assertEqual(result["overall_action"], "lower_trust")
        self.assertEqual(result["lowered_trust_chunk_ids"], ["chunk_2"])

    def test_multiple_user_query_issues_escalate_to_refusal(self):
        result = self.service.decide(
            [
                {"issue_scope": "user_query", "risk_score": 66, "recommended_action": "warn"},
                {"issue_scope": "user_query", "risk_score": 68, "recommended_action": "warn"},
            ]
        )
        self.assertEqual(result["overall_action"], "refuse")
        self.assertEqual(result["prompt_injection_result"], "refused")


if __name__ == "__main__":
    unittest.main()
