from __future__ import annotations

import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(KeyError)
    async def handle_key_error(_: Request, exc: KeyError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc), "request_id": str(uuid.uuid4())},
        )

    @app.exception_handler(ValueError)
    async def handle_value_error(_: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc), "request_id": str(uuid.uuid4())},
        )
