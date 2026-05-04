from dataclasses import dataclass


@dataclass
class IngestionAttempt:
    attempt_id: str
    document_id: str | None
    source_type: str
    source_identifier: str | None
    status: str
    duplicate_class: str | None
    error_message: str | None
    user_decision: str | None
    payload_json: str | None
    created_at: str
    updated_at: str
