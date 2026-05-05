from dataclasses import dataclass


@dataclass
class ChatSession:
    session_id: str
    user_id: str | None
    selected_collection_id: str | None
    retrieval_mode: str
    metadata_json: str | None
    created_at: str
    updated_at: str

    @classmethod
    def from_row(cls, row):
        return cls(
            session_id=row["session_id"],
            user_id=row.get("user_id"),
            selected_collection_id=row.get("selected_collection_id"),
            retrieval_mode=row["retrieval_mode"],
            metadata_json=row.get("metadata_json"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "collection_id": self.selected_collection_id,
            "retrieval_mode": self.retrieval_mode,
            "metadata_json": self.metadata_json,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
