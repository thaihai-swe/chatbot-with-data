import re


class SafetyScannerService:
    def __init__(self, rules=None):
        self.rules = [
            {
                **rule,
                "compiled_pattern": re.compile(rule["pattern"], re.IGNORECASE),
            }
            for rule in (rules or [])
        ]

    def _recommended_action(self, scope, risk_score):
        if scope == "user_query":
            return "refuse" if risk_score >= 90 else "warn"
        if risk_score >= 85:
            return "exclude_chunk"
        if risk_score >= 60:
            return "lower_trust"
        if risk_score >= 30:
            return "warn"
        return "ignore"

    def _scan_text(self, text, scope, document_id=None, chunk_id=None):
        content = text or ""
        issues = []
        for rule in self.rules:
            match = rule["compiled_pattern"].search(content)
            if not match:
                continue
            issues.append(
                {
                    "issue_scope": scope,
                    "detection_method": "rule_pattern",
                    "matched_pattern": rule["name"],
                    "classifier_reason": f"Matched rule `{rule['name']}`",
                    "risk_score": float(rule["risk_score"]),
                    "affected_document_id": document_id,
                    "affected_chunk_id": chunk_id,
                    "recommended_action": self._recommended_action(scope, rule["risk_score"]),
                    "content_snippet": content[:240],
                }
            )
        return issues

    def scan_user_query(self, question_text):
        return self._scan_text(question_text, "user_query")

    def scan_retrieved_chunks(self, chunks):
        issues = []
        for chunk in chunks or []:
            issues.extend(
                self._scan_text(
                    chunk.get("full_text") or chunk.get("content_snippet"),
                    "retrieved_chunk",
                    document_id=chunk.get("document_id"),
                    chunk_id=chunk.get("chunk_id"),
                )
            )
        return issues
