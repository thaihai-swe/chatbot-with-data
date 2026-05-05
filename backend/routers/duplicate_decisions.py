from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ingestion.service import IngestionService
from models import IngestionStatus
from schemas.documents import DuplicateDecisionRequest


router = APIRouter(prefix="/ingestion/attempts", tags=["duplicate-decisions"])
service = IngestionService()


@router.post("/{attempt_id}/duplicate-decision", response_model=dict)
def decide_duplicate(attempt_id: str, payload: DuplicateDecisionRequest) -> dict:
    attempt = service.repository.get_ingestion_attempt(attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Ingestion attempt not found")
    if attempt["status"] != IngestionStatus.AWAITING_USER_ACTION.value:
        raise HTTPException(
            status_code=409,
            detail="Duplicate decision is only available for attempts awaiting user action",
        )
    return service.apply_duplicate_decision(attempt_id, payload.action.value)
