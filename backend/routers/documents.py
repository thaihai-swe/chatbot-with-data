from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from indexing.weaviate_store import WeaviateVectorStore
from repositories import Repository
from schemas.documents import (
    DocumentMoveRequest,
    DocumentResponse,
    DocumentSummary,
    ReingestRequest,
)

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/documents", tags=["documents"])
repository = Repository()


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
def delete_document(document_id: str) -> None:
    if not repository.delete_document(document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    # Vector cleanup after successful SQL deletion
    try:
        weaviate_store = WeaviateVectorStore()
        deleted = weaviate_store.delete_by_document(document_id)
        logger.info(f"Deleted {deleted} vectors for document {document_id}")
    except Exception as exc:
        logger.error(f"Vector deletion failed for document {document_id}: {exc}")
        raise HTTPException(status_code=500, detail="Vector deletion failed")


@router.post("/{document_id}/move", response_model=DocumentResponse)
def move_document(document_id: str, payload: DocumentMoveRequest) -> dict:
    record = repository.get_document(document_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    repository.assign_document_to_collections(document_id, payload.collection_ids)
    return repository.get_document(document_id)


@router.post("/{document_id}/reindex", response_model=dict)
def reindex_document(document_id: str) -> dict[str, str]:
    from ingestion.service import IngestionService
    record = repository.get_document(document_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")

    repository.record_reindex_request(document_id)

    # Trigger actual indexing
    ingestion_service = IngestionService()

    # We need to pass an attempt-like dict or just fetch what's needed
    attempt_mock = {
        "extracted_text": record["extracted_text"],
        "source_type": record["source_type"],
        "collection_ids": [c["id"] for c in record["collections"]],
        "title": record["title"],
        "submitted_filename": record["filename"],
    }

    ingestion_service._chunk_and_index_document(document_id, attempt_mock)

    return {
        "document_id": document_id,
        "status": "completed",
        "message": "Document re-indexed successfully.",
    }


@router.post("/{document_id}/reingest", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
def reingest_document(document_id: str, payload: ReingestRequest) -> dict:
    try:
        attempt = repository.create_reingest_attempt(
            document_id=document_id,
            collection_ids=payload.collection_ids,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return attempt
