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
    settings_router,
)

def create_app() -> FastAPI:
    # 1. Basic config
    settings = get_settings()
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 2. Middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = request.headers.get(settings.request_id_header, str(uuid.uuid4()))
        response = await call_next(request)
        response.headers[settings.request_id_header] = request_id
        return response

    # 3. Router registration
    app.include_router(collections_router)
    app.include_router(documents_router)
    app.include_router(duplicate_decisions_router)
    app.include_router(health_router)
    app.include_router(ingestion_router)
    app.include_router(chat_router)
    app.include_router(settings_router)

    # 4. Error handlers
    register_error_handlers(app)

    # 5. Startup events
    @app.on_event("startup")
    async def startup_event():
        apply_migrations()
        # Any other startup logic

    return app

app = create_app()
