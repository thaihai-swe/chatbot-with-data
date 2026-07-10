from __future__ import annotations

import json
import uuid
from typing import List, Dict, Any, Optional

from database import get_connection
from schemas.chat import SanityCheckResponse

class EvaluationRepository:
    @staticmethod
    def save_run(
        dataset_name: str,
        model_name: str,
        total_cases: int,
        passed_cases: int,
        overall_recall: float,
        overall_groundedness: float,
        config_variant_name: Optional[str] = None,
        config_snapshot_json: Optional[str] = None
    ) -> str:
        run_id = str(uuid.uuid4())
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO evaluation_runs (
                    id, dataset_name, model_name, total_cases, passed_cases, 
                    overall_recall, overall_groundedness,
                    config_variant_name, config_snapshot_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    dataset_name,
                    model_name,
                    total_cases,
                    passed_cases,
                    overall_recall,
                    overall_groundedness,
                    config_variant_name,
                    config_snapshot_json
                )
            )
        return run_id

    @staticmethod
    def list_recent_runs(limit: int = 10) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM evaluation_runs
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
