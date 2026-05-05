class SafetyDecisionService:
    def __init__(
        self,
        warn_threshold=30,
        lower_trust_threshold=55,
        exclude_threshold=70,
        refuse_threshold=90,
        multi_issue_refuse_total=130,
    ):
        self.warn_threshold = warn_threshold
        self.lower_trust_threshold = lower_trust_threshold
        self.exclude_threshold = exclude_threshold
        self.refuse_threshold = refuse_threshold
        self.multi_issue_refuse_total = multi_issue_refuse_total

    def _action_for_issue(self, issue):
        risk = float(issue.get("risk_score", 0))
        scope = issue.get("issue_scope")
        if scope == "user_query":
            if risk >= self.refuse_threshold:
                return "refuse"
            if risk >= self.warn_threshold:
                return "warn"
            return "ignore"
        if risk >= self.exclude_threshold:
            return "exclude_chunk"
        if risk >= self.lower_trust_threshold:
            return "lower_trust"
        if risk >= self.warn_threshold:
            return "warn"
        return "ignore"

    def decide(self, issues):
        enriched = []
        actionable = []
        total_risk = 0.0
        max_risk = 0.0
        has_user_query_issue = False
        for issue in issues or []:
            final_action = self._action_for_issue(issue)
            enriched_issue = {**issue, "final_action": final_action}
            enriched.append(enriched_issue)
            if final_action != "ignore":
                actionable.append(enriched_issue)
                total_risk += float(enriched_issue.get("risk_score", 0))
                max_risk = max(max_risk, float(enriched_issue.get("risk_score", 0)))
                has_user_query_issue = has_user_query_issue or enriched_issue.get("issue_scope") == "user_query"

        overall_action = "ignore"
        if any(issue["final_action"] == "refuse" for issue in actionable):
            overall_action = "refuse"
        elif has_user_query_issue and len(actionable) >= 2 and total_risk >= self.multi_issue_refuse_total:
            overall_action = "refuse"
            enriched = [
                {**issue, "final_action": "refuse" if issue["final_action"] != "ignore" else "ignore"}
                for issue in enriched
            ]
        elif any(issue["final_action"] == "exclude_chunk" for issue in actionable):
            overall_action = "exclude_chunk"
        elif any(issue["final_action"] == "lower_trust" for issue in actionable):
            overall_action = "lower_trust"
        elif any(issue["final_action"] == "warn" for issue in actionable):
            overall_action = "warn"

        excluded_chunk_ids = [
            issue["affected_chunk_id"]
            for issue in enriched
            if issue["final_action"] in {"exclude_chunk", "refuse"} and issue.get("affected_chunk_id")
        ]
        lowered_trust_chunk_ids = [
            issue["affected_chunk_id"]
            for issue in enriched
            if issue["final_action"] == "lower_trust" and issue.get("affected_chunk_id")
        ]

        prompt_injection_result = "clear"
        if overall_action == "refuse":
            prompt_injection_result = "refused"
        elif excluded_chunk_ids:
            prompt_injection_result = "excluded_chunks"
        elif lowered_trust_chunk_ids:
            prompt_injection_result = "lowered_trust"
        elif actionable:
            prompt_injection_result = "warning"

        warning_summary = None
        excluded_evidence_notice = None
        if overall_action == "refuse":
            warning_summary = "The system refused this run because it detected instruction-like or prompt-injection content."
        elif excluded_chunk_ids:
            warning_summary = f"The system excluded {len(excluded_chunk_ids)} suspicious evidence chunk(s) before answering."
            excluded_evidence_notice = warning_summary
        elif lowered_trust_chunk_ids:
            warning_summary = "The system answered cautiously because some evidence was treated as lower trust."
        elif actionable:
            warning_summary = "The system detected suspicious instruction-like content and answered with warnings."

        return {
            "issues": enriched,
            "overall_action": overall_action,
            "prompt_injection_result": prompt_injection_result,
            "prompt_injection_risk_score": max_risk,
            "safety_issue_count": len(actionable),
            "warning_summary": warning_summary,
            "excluded_evidence_notice": excluded_evidence_notice,
            "excluded_chunk_ids": excluded_chunk_ids,
            "lowered_trust_chunk_ids": lowered_trust_chunk_ids,
        }

    def apply_to_chunks(self, chunks, decision):
        selected = []
        excluded = []
        lowered_trust_ids = set(decision.get("lowered_trust_chunk_ids") or [])
        excluded_ids = set(decision.get("excluded_chunk_ids") or [])
        reasons_by_chunk = {}
        for issue in decision.get("issues", []):
            if issue.get("affected_chunk_id") and issue.get("final_action") in {"exclude_chunk", "refuse"}:
                reasons_by_chunk.setdefault(issue["affected_chunk_id"], []).append(issue["matched_pattern"])

        for chunk in chunks or []:
            chunk_id = chunk.get("chunk_id")
            if chunk_id in excluded_ids:
                excluded.append(
                    {
                        **chunk,
                        "exclusion_reason": ", ".join(reasons_by_chunk.get(chunk_id, [])) or "suspicious instruction-like content",
                    }
                )
                continue
            next_chunk = dict(chunk)
            if chunk_id in lowered_trust_ids:
                next_chunk["retrieval_score"] = round((next_chunk.get("retrieval_score", 0.0) or 0.0) * 0.65, 4)
                next_chunk["lowered_trust"] = True
            selected.append(next_chunk)
        return selected, excluded
