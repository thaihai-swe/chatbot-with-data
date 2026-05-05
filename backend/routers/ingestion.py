from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status

from ingestion.service import IngestionService
from schemas import IngestionAttemptResponse, UrlIngestionRequest


router = APIRouter(prefix="/ingestion", tags=["ingestion"])
service = IngestionService()


@router.post(
    "/file-upload",
    response_model=IngestionAttemptResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    collection_ids: str = Form(default=""),
) -> dict:
    parsed_collection_ids = [item for item in collection_ids.split(",") if item]
    attempt = await service.submit_file_upload(
        file=file,
        collection_ids=parsed_collection_ids,
    )
    background_tasks.add_task(service.process_ingestion_attempt, attempt["id"])
    return attempt


@router.post("/url", response_model=IngestionAttemptResponse, status_code=status.HTTP_202_ACCEPTED)
def ingest_url(payload: UrlIngestionRequest, background_tasks: BackgroundTasks) -> dict:
    attempt = service.submit_url(payload.url.unicode_string(), payload.collection_ids)
    background_tasks.add_task(service.process_ingestion_attempt, attempt["id"])
    return attempt


@router.get("/attempts", response_model=list[IngestionAttemptResponse])
def list_attempts(status: str | None = None) -> list[dict]:
    return service.repository.list_ingestion_attempts(status=status)


@router.get("/attempts/{attempt_id}", response_model=IngestionAttemptResponse)
def get_attempt(attempt_id: str) -> dict:
    attempt = service.repository.get_ingestion_attempt(attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Ingestion attempt not found")
    return attempt
