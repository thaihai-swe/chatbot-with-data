from dataclasses import dataclass


@dataclass
class ChatMessage:
    message_id: str
    session_id: str
    turn_id: str | None
    turn_order: int
    role: str
    content: str
    answer_status: str
    refusal_category: str | None
    retrieval_mode_used: str | None
    created_at: str
    updated_at: str

    @classmethod
    def from_row(cls, row):
        return cls(
            message_id=row["message_id"],
            session_id=row["session_id"],
            turn_id=row.get("turn_id"),
            turn_order=row["turn_order"],
            role=row["role"],
            content=row["content"],
            answer_status=row["answer_status"],
            refusal_category=row.get("refusal_category"),
            retrieval_mode_used=row.get("retrieval_mode_used"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "session_id": self.session_id,
            "turn_id": self.turn_id,
            "turn_order": self.turn_order,
            "role": self.role,
            "content": self.content,
            "answer_status": self.answer_status,
            "refusal_category": self.refusal_category,
            "retrieval_mode_used": self.retrieval_mode_used,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
