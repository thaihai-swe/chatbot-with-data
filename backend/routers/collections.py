from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from repositories import Repository
from schemas import CollectionCreate, CollectionResponse, CollectionUpdate


router = APIRouter(prefix="/collections", tags=["collections"])
repository = Repository()


@router.get("", response_model=list[CollectionResponse])
def list_collections() -> list[dict]:
    return repository.list_collections()


@router.post("", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection(payload: CollectionCreate) -> dict:
    try:
        return repository.create_collection(**payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{collection_id}", response_model=CollectionResponse)
def get_collection(collection_id: str) -> dict:
    record = repository.get_collection(collection_id)
    if not record:
        raise HTTPException(status_code=404, detail="Collection not found")
    return record


@router.patch("/{collection_id}", response_model=CollectionResponse)
def update_collection(collection_id: str, payload: CollectionUpdate) -> dict:
    record = repository.update_collection(collection_id, **payload.model_dump())
    if not record:
        raise HTTPException(status_code=404, detail="Collection not found")
    return record


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(collection_id: str) -> None:
    if not repository.delete_collection(collection_id):
        raise HTTPException(status_code=404, detail="Collection not found")
