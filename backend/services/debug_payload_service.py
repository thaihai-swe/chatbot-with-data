class DebugPayloadService:
    def __init__(self, run_record_service):
        self.run_record_service = run_record_service

    def build_payload(self, run_id):
        record = self.run_record_service.get_run_record(run_id)
        if not record:
            return None
        issues = self.run_record_service.list_safety_issues(run_id)
        snapshot = self.run_record_service.get_debug_snapshot(run_id)
        payload = {
            "run_id": record["run_id"],
            "turn_id": record["turn_id"],
            "session_id": record["session_id"],
            "original_query": record["query_text"],
            "rewritten_query": snapshot.get("rewritten_query"),
            "query_mode": snapshot.get("query_mode", "original"),
            "retrieval_mode": record.get("retrieval_mode_used"),
            "collection_id": record.get("selected_collection_id"),
            "retrieval_filters": snapshot.get("retrieval_filters") or {
                "collection_id": record.get("selected_collection_id"),
            },
            "all_retrieved_chunks": snapshot.get("all_retrieved_chunks", []),
            "selected_context_chunks": snapshot.get("selected_context_chunks", []),
            "excluded_chunks_with_reasons": snapshot.get("excluded_chunks_with_reasons", []),
            "citations": snapshot.get("citations", []),
            "final_answer_or_refusal": snapshot.get("final_answer_or_refusal")
            or {
                "result_type": record["result_type"],
                "answer_text": record.get("answer_text"),
                "refusal_text": record.get("answer_text") if record["result_type"] == "refusal" else None,
                "refusal_reason": record.get("refusal_reason"),
            },
            "groundedness_status": record["groundedness_status"],
            "answerability_flag": record["answerability_flag"],
            "answerability_score": record.get("answerability_score"),
            "answerability": record.get("answerability") or {},
            "prompt_injection_result": record["prompt_injection_result"],
            "prompt_injection_risk_score": record["prompt_injection_risk_score"],
            "all_safety_issues": issues,
            "safety_decision": snapshot.get("safety_decision")
            or {
                "prompt_injection_result": record["prompt_injection_result"],
                "warning_summary": record.get("warning_summary"),
                "excluded_evidence_notice": record.get("excluded_evidence_notice"),
            },
            "latency_ms": record["latency_ms"],
            "token_count": record["token_count"],
            "model_name": record.get("model_name"),
            "embedding_model_name": record.get("embedding_model"),
            "warning_summary": record.get("warning_summary"),
            "excluded_evidence_notice": record.get("excluded_evidence_notice"),
            "response_payload": snapshot.get("response_payload"),
            "created_at": record["created_at"],
        }
        return payload
