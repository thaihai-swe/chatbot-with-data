import json

from backend.models.run_record import RunRecord
from backend.models.safety_issue import SafetyIssue
from backend.persistence.db import get_connection
from backend.utils import generate_id, json_dumps, utcnow_iso


class RunRecordService:
    def __init__(self, sqlite_path):
        self.sqlite_path = sqlite_path

    def create_run_record(
        self,
        *,
        turn_id,
        session_id,
        query_text,
        answer_text,
        refusal_reason,
        answerability_flag,
        answerability_score,
        groundedness_status,
        prompt_injection_result,
        prompt_injection_risk_score,
        safety_issues,
        latency_ms,
        token_count,
        model_name,
        embedding_model,
        retrieval_mode_used,
        selected_collection_id,
        result_type,
        warning_summary,
        excluded_evidence_notice,
        retrieval_metadata,
        generation_metadata,
        answerability,
        debug_snapshot,
        observability_metadata=None,
    ):
        run_id = generate_id("run")
        now = utcnow_iso()
        snapshot_payload = dict(debug_snapshot or {})
        if isinstance(snapshot_payload.get("response_payload"), dict):
            snapshot_payload["response_payload"] = {
                **snapshot_payload["response_payload"],
                "run_id": run_id,
            }
        with get_connection(self.sqlite_path) as connection:
            connection.execute(
                """
                INSERT INTO run_records (
                    run_id, turn_id, session_id, query_text, answer_text, refusal_reason,
                    answerability_flag, answerability_score, groundedness_status,
                    prompt_injection_result, prompt_injection_risk_score, safety_issue_count,
                    latency_ms, token_count, model_name, embedding_model, retrieval_mode_used,
                    selected_collection_id, result_type, warning_summary, excluded_evidence_notice,
                    retrieval_metadata_json, generation_metadata_json, answerability_json,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    turn_id,
                    session_id,
                    query_text,
                    answer_text,
                    refusal_reason,
                    1 if answerability_flag else 0,
                    answerability_score,
                    groundedness_status,
                    prompt_injection_result,
                    prompt_injection_risk_score,
                    len(safety_issues or []),
                    latency_ms,
                    token_count,
                    model_name,
                    embedding_model,
                    retrieval_mode_used,
                    selected_collection_id,
                    result_type,
                    warning_summary,
                    excluded_evidence_notice,
                    json_dumps(retrieval_metadata or {}),
                    json_dumps(generation_metadata or {}),
                    json_dumps(answerability or {}),
                    now,
                    now,
                ),
            )
            for issue in safety_issues or []:
                connection.execute(
                    """
                    INSERT INTO safety_issues (
                        issue_id, run_id, issue_scope, detection_method, risk_score,
                        matched_pattern, classifier_reason, affected_document_id, affected_chunk_id,
                        recommended_action, final_action, final_decision, content_snippet, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        generate_id("safety"),
                        run_id,
                        issue.get("issue_scope"),
                        issue.get("detection_method"),
                        issue.get("risk_score", 0.0),
                        issue.get("matched_pattern"),
                        issue.get("classifier_reason"),
                        issue.get("affected_document_id"),
                        issue.get("affected_chunk_id"),
                        issue.get("recommended_action"),
                        issue.get("final_action"),
                        issue.get("final_decision") or issue.get("final_action"),
                        issue.get("content_snippet"),
                        now,
                    ),
                )
            connection.execute(
                """
                INSERT INTO debug_snapshots (run_id, snapshot_json, created_at)
                VALUES (?, ?, ?)
                """,
                (run_id, json_dumps(snapshot_payload), now),
            )
            for key, value in (observability_metadata or {}).items():
                connection.execute(
                    """
                    INSERT INTO observability_metadata (
                        metadata_id, run_id, metadata_key, metadata_value_json, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (generate_id("meta"), run_id, key, json_dumps(value), now),
                )
        return self.get_run_record(run_id)

    def get_run_record(self, run_id):
        with get_connection(self.sqlite_path) as connection:
            row = connection.execute("SELECT * FROM run_records WHERE run_id = ?", (run_id,)).fetchone()
        if not row:
            return None
        payload = RunRecord.from_row(row).to_dict()
        payload["retrieval_metadata"] = json.loads(row.get("retrieval_metadata_json") or "{}")
        payload["generation_metadata"] = json.loads(row.get("generation_metadata_json") or "{}")
        payload["answerability"] = json.loads(row.get("answerability_json") or "{}")
        return payload

    def get_run_by_turn(self, turn_id):
        with get_connection(self.sqlite_path) as connection:
            row = connection.execute("SELECT run_id FROM run_records WHERE turn_id = ?", (turn_id,)).fetchone()
        if not row:
            return None
        return self.get_run_record(row["run_id"])

    def list_runs_for_session(self, session_id):
        with get_connection(self.sqlite_path) as connection:
            rows = connection.execute(
                "SELECT * FROM run_records WHERE session_id = ? ORDER BY created_at DESC",
                (session_id,),
            ).fetchall()
        return [self.get_run_record(row["run_id"]) for row in rows]

    def list_safety_issues(self, run_id):
        with get_connection(self.sqlite_path) as connection:
            rows = connection.execute(
                "SELECT * FROM safety_issues WHERE run_id = ? ORDER BY created_at ASC",
                (run_id,),
            ).fetchall()
        return [SafetyIssue.from_row(row).to_dict() for row in rows]

    def get_debug_snapshot(self, run_id):
        with get_connection(self.sqlite_path) as connection:
            row = connection.execute(
                "SELECT snapshot_json FROM debug_snapshots WHERE run_id = ?",
                (run_id,),
            ).fetchone()
        if not row:
            return {}
        return json.loads(row.get("snapshot_json") or "{}")
