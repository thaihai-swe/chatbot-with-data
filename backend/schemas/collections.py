from __future__ import annotations

from pydantic import BaseModel, Field


class CollectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    is_default: bool = False
    routing_enabled: bool = False


class CollectionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    is_default: bool | None = None
    routing_enabled: bool | None = None


class CollectionResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    is_default: bool
    routing_enabled: bool
    document_count: int = 0
    created_at: str
    updated_at: str
