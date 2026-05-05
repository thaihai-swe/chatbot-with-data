from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Knowledge Ingestion API")
    environment: str = os.getenv("APP_ENV", "development")
    data_dir: Path = Path(os.getenv("DATA_DIR", "data/knowledge_ingestion"))
    database_path: Path = Path(
        os.getenv("DATABASE_PATH", "data/knowledge_ingestion/app.db")
    )
    uploads_dir: Path = Path(
        os.getenv("UPLOADS_DIR", "data/knowledge_ingestion/uploads")
    )
    snapshots_dir: Path = Path(
        os.getenv("SNAPSHOTS_DIR", "data/knowledge_ingestion/snapshots")
    )
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    )
    request_id_header: str = "X-Request-ID"
    url_timeout_seconds: int = int(os.getenv("URL_TIMEOUT_SECONDS", "10"))

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
