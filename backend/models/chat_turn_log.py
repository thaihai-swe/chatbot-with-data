from dataclasses import dataclass


@dataclass
class ChatTurnLog:
    log_id: str
    turn_id: str
    session_id: str
    question_text: str
    retrieval_mode_used: str
    retrieved_chunk_count: int
    answerability_score: float | None
    refusal_category: str | None
    answer_length_tokens: int
    final_citation_count: int
    metadata_json: str | None
    created_at: str

    def to_dict(self):
        return {
            "log_id": self.log_id,
            "turn_id": self.turn_id,
            "session_id": self.session_id,
            "question_text": self.question_text,
            "retrieval_mode_used": self.retrieval_mode_used,
            "retrieved_chunk_count": self.retrieved_chunk_count,
            "answerability_score": self.answerability_score,
            "refusal_category": self.refusal_category,
            "answer_length_tokens": self.answer_length_tokens,
            "final_citation_count": self.final_citation_count,
            "metadata_json": self.metadata_json,
            "created_at": self.created_at,
        }
