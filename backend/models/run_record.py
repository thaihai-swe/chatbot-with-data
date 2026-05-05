from dataclasses import dataclass


@dataclass
class RunRecord:
    run_id: str
    turn_id: str
    session_id: str
    query_text: str
    answer_text: str | None
    refusal_reason: str | None
    answerability_flag: int
    answerability_score: float | None
    groundedness_status: str
    prompt_injection_result: str
    prompt_injection_risk_score: float
    safety_issue_count: int
    latency_ms: int
    token_count: int
    model_name: str | None
    embedding_model: str | None
    retrieval_mode_used: str | None
    selected_collection_id: str | None
    result_type: str
    warning_summary: str | None
    excluded_evidence_notice: str | None
    retrieval_metadata_json: str | None
    generation_metadata_json: str | None
    answerability_json: str | None
    created_at: str
    updated_at: str

    @classmethod
    def from_row(cls, row):
        return cls(
            run_id=row["run_id"],
            turn_id=row["turn_id"],
            session_id=row["session_id"],
            query_text=row["query_text"],
            answer_text=row.get("answer_text"),
            refusal_reason=row.get("refusal_reason"),
            answerability_flag=row.get("answerability_flag", 0),
            answerability_score=row.get("answerability_score"),
            groundedness_status=row["groundedness_status"],
            prompt_injection_result=row["prompt_injection_result"],
            prompt_injection_risk_score=row.get("prompt_injection_risk_score", 0.0),
            safety_issue_count=row.get("safety_issue_count", 0),
            latency_ms=row.get("latency_ms", 0),
            token_count=row.get("token_count", 0),
            model_name=row.get("model_name"),
            embedding_model=row.get("embedding_model"),
            retrieval_mode_used=row.get("retrieval_mode_used"),
            selected_collection_id=row.get("selected_collection_id"),
            result_type=row["result_type"],
            warning_summary=row.get("warning_summary"),
            excluded_evidence_notice=row.get("excluded_evidence_notice"),
            retrieval_metadata_json=row.get("retrieval_metadata_json"),
            generation_metadata_json=row.get("generation_metadata_json"),
            answerability_json=row.get("answerability_json"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self):
        return {
            "run_id": self.run_id,
            "turn_id": self.turn_id,
            "session_id": self.session_id,
            "query_text": self.query_text,
            "answer_text": self.answer_text,
            "refusal_reason": self.refusal_reason,
            "answerability_flag": bool(self.answerability_flag),
            "answerability_score": self.answerability_score,
            "groundedness_status": self.groundedness_status,
            "prompt_injection_result": self.prompt_injection_result,
            "prompt_injection_risk_score": self.prompt_injection_risk_score,
            "safety_issue_count": self.safety_issue_count,
            "latency_ms": self.latency_ms,
            "token_count": self.token_count,
            "model_name": self.model_name,
            "embedding_model": self.embedding_model,
            "retrieval_mode_used": self.retrieval_mode_used,
            "selected_collection_id": self.selected_collection_id,
            "result_type": self.result_type,
            "warning_summary": self.warning_summary,
            "excluded_evidence_notice": self.excluded_evidence_notice,
            "retrieval_metadata_json": self.retrieval_metadata_json,
            "generation_metadata_json": self.generation_metadata_json,
            "answerability_json": self.answerability_json,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
