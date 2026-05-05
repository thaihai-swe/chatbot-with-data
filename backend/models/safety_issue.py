from dataclasses import dataclass


@dataclass
class SafetyIssue:
    issue_id: str
    run_id: str
    issue_scope: str
    detection_method: str
    risk_score: float
    matched_pattern: str | None
    classifier_reason: str | None
    affected_document_id: str | None
    affected_chunk_id: str | None
    recommended_action: str
    final_action: str
    final_decision: str | None
    content_snippet: str | None
    created_at: str

    @classmethod
    def from_row(cls, row):
        return cls(
            issue_id=row["issue_id"],
            run_id=row["run_id"],
            issue_scope=row["issue_scope"],
            detection_method=row["detection_method"],
            risk_score=row["risk_score"],
            matched_pattern=row.get("matched_pattern"),
            classifier_reason=row.get("classifier_reason"),
            affected_document_id=row.get("affected_document_id"),
            affected_chunk_id=row.get("affected_chunk_id"),
            recommended_action=row["recommended_action"],
            final_action=row["final_action"],
            final_decision=row.get("final_decision"),
            content_snippet=row.get("content_snippet"),
            created_at=row["created_at"],
        )

    def to_dict(self):
        return {
            "issue_id": self.issue_id,
            "run_id": self.run_id,
            "issue_scope": self.issue_scope,
            "detection_method": self.detection_method,
            "risk_score": self.risk_score,
            "matched_pattern": self.matched_pattern,
            "classifier_reason": self.classifier_reason,
            "affected_document_id": self.affected_document_id,
            "affected_chunk_id": self.affected_chunk_id,
            "recommended_action": self.recommended_action,
            "final_action": self.final_action,
            "final_decision": self.final_decision,
            "content_snippet": self.content_snippet,
            "created_at": self.created_at,
        }
