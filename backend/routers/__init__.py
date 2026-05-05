from routers.collections import router as collections_router
from routers.documents import router as documents_router
from routers.duplicate_decisions import router as duplicate_decisions_router
from routers.health import router as health_router
from routers.ingestion import router as ingestion_router

__all__ = [
    "collections_router",
    "documents_router",
    "duplicate_decisions_router",
    "health_router",
    "ingestion_router",
]
