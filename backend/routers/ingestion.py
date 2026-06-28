from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status

from ingestion.service import IngestionService
from repositories import IngestionRepository
from schemas import IngestionAttemptResponse, UrlIngestionRequest


router = APIRouter(prefix="/ingestion", tags=["ingestion"])
ingestion_repo = IngestionRepository()


def get_ingestion_service() -> IngestionService:
    return IngestionService()


@router.post(
    "/file-upload",
    response_model=IngestionAttemptResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    collection_ids: str = Form(default=""),
    svc: IngestionService = Depends(get_ingestion_service),
) -> dict:
    parsed_collection_ids = [item for item in collection_ids.split(",") if item]
    attempt = await svc.submit_file_upload(
        file=file,
        collection_ids=parsed_collection_ids,
    )
    background_tasks.add_task(svc.process_ingestion_attempt, attempt["id"])
    return attempt


@router.post("/url", response_model=IngestionAttemptResponse, status_code=status.HTTP_202_ACCEPTED)
def ingest_url(
    payload: UrlIngestionRequest,
    background_tasks: BackgroundTasks,
    svc: IngestionService = Depends(get_ingestion_service),
) -> dict:
    attempt = svc.submit_url(payload.url.unicode_string(), payload.collection_ids)
    background_tasks.add_task(svc.process_ingestion_attempt, attempt["id"])
    return attempt


@router.get("/attempts", response_model=list[IngestionAttemptResponse])
def list_attempts(status: str | None = None) -> list[dict]:
    return ingestion_repo.list_ingestion_attempts(status=status)


@router.get("/attempts/{attempt_id}", response_model=IngestionAttemptResponse)
def get_attempt(attempt_id: str) -> dict:
    attempt = ingestion_repo.get_ingestion_attempt(attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Ingestion attempt not found")
    return attempt
