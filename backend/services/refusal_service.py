REFUSAL_TEMPLATES = {
    "no_relevant_evidence": "I don't have any documents that match this question.",
    "low_confidence": "I found some related information, but I'm not confident enough to answer this question.",
    "insufficient_support": "The available documents don't have enough information to answer this comprehensively.",
    "conflicting_evidence": "The documents contain conflicting information on this topic.",
    "out_of_domain": "This question is outside the scope of available documents.",
    "prompt_injection_risk": "I refused this request because it contains instruction-like content that could override the system's grounding rules.",
}


class RefusalService:
    def generate_refusal(self, answerability_result):
        reason = answerability_result["reason_category"] or "no_relevant_evidence"
        return {
            "refusal_text": REFUSAL_TEMPLATES[reason],
            "reason_category": reason,
            "supporting_metrics": answerability_result.get("supporting_metrics", {}),
            "suggestion_for_user": "Try asking a narrower question or selecting a different collection.",
        }
