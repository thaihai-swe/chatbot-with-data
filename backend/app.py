from __future__ import annotations

import uuid
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings, configure_logging
from error_handlers import register_error_handlers
from migrations import apply_migrations
from routers import (
    collections_router,
    documents_router,
    duplicate_decisions_router,
    health_router,
    ingestion_router,
    chat_router,
    evaluation_router,
)
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    # Configure logging FIRST, before any other operations
    configure_logging()
    logger = logging.getLogger(__name__)

    settings = get_settings()
    logger.info(f"Starting application in {settings.environment} mode with log level: {settings.log_level}")
    apply_migrations()
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Allows all origins
    allow_credentials=True,   # Note: Cannot be True if allow_origins=["*"] for some browsers
    allow_methods=["*"],      # Allows all methods
    allow_headers=["*"],      # Allows all headers
    )
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = request.headers.get(settings.request_id_header, str(uuid.uuid4()))
        response = await call_next(request)
        response.headers[settings.request_id_header] = request_id
        return response

    app.include_router(health_router)
    app.include_router(collections_router)
    app.include_router(documents_router)
    app.include_router(ingestion_router)
    app.include_router(duplicate_decisions_router)
    app.include_router(chat_router)
    app.include_router(evaluation_router)
    register_error_handlers(app)
    return app


app = create_app()
