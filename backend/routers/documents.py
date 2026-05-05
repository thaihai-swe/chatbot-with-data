from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from repositories import Repository
from schemas.documents import (
    DocumentMoveRequest,
    DocumentResponse,
    DocumentSummary,
    ReingestRequest,
)


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


@router.post("/{document_id}/move", response_model=DocumentResponse)
def move_document(document_id: str, payload: DocumentMoveRequest) -> dict:
    record = repository.get_document(document_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    repository.assign_document_to_collections(document_id, payload.collection_ids)
    return repository.get_document(document_id)


@router.post("/{document_id}/reindex", response_model=dict)
def reindex_document(document_id: str) -> dict[str, str]:
    record = repository.get_document(document_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    repository.record_reindex_request(document_id)
    return {
        "document_id": document_id,
        "status": "recorded",
        "message": "Re-index initiation recorded as a forward-compatible placeholder.",
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
