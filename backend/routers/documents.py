from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from ingestion.service import IngestionService
from repositories import DocumentRepository, IngestionRepository
from schemas.documents import (
    DocumentMoveRequest,
    DocumentResponse,
    DocumentSummary,
    ReingestRequest,
)

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/documents", tags=["documents"])
repository = DocumentRepository()


def get_ingestion_service() -> IngestionService:
    return IngestionService()


@router.get("", response_model=list[DocumentSummary])
def list_documents(
    collection_id: str | None = None,
    query: str | None = None,
) -> list[dict]:
    return repository.list_documents(collection_id=collection_id, search_query=query)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str) -> dict:
    record = repository.get_document(document_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    return record


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    svc: IngestionService = Depends(get_ingestion_service),
) -> None:
    if not repository.delete_document(document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    svc.delete_document_vectors(document_id)


@router.post("/{document_id}/move", response_model=DocumentResponse)
def move_document(document_id: str, payload: DocumentMoveRequest) -> dict:
    record = repository.get_document(document_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    repository.assign_document_to_collections(document_id, payload.collection_ids)
    return repository.get_document(document_id)


@router.post("/{document_id}/reindex", response_model=dict)
def reindex_document(
    document_id: str,
    svc: IngestionService = Depends(get_ingestion_service),
) -> dict[str, str]:
    record = repository.get_document(document_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")

    repository.record_reindex_request(document_id)

    attempt_mock = {
        "extracted_text": record["extracted_text"],
        "source_type": record["source_type"],
        "collection_ids": [c["id"] for c in record["collections"]],
        "title": record["title"],
        "submitted_filename": record["filename"],
    }

    svc.chunk_and_index_document(document_id, attempt_mock)

    return {
        "document_id": document_id,
        "status": "completed",
        "message": "Document re-indexed successfully.",
    }


@router.post("/{document_id}/reingest", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
def reingest_document(
    document_id: str,
    payload: ReingestRequest,
    svc: IngestionService = Depends(get_ingestion_service),
) -> dict:
    try:
        attempt = IngestionRepository().create_reingest_attempt(
            document_id=document_id,
            collection_ids=payload.collection_ids,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    svc.process_ingestion_attempt(attempt["id"])
    return attempt
