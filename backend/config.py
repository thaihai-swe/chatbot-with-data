from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

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

    # LLM Settings
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_api_base: Optional[str] = os.getenv("OPENAI_API_BASE")
    chat_model: str = os.getenv("CHAT_MODEL", "gpt-4o")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # Chroma Settings
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", ".chroma_db")
    chroma_collection_name: str = os.getenv("CHROMA_COLLECTION_NAME", "document-chunks")

    # RAG Settings
    context_window_size: int = int(os.getenv("CONTEXT_WINDOW_SIZE", "128000"))
    max_history_turns: int = int(os.getenv("MAX_HISTORY_TURNS", "10"))
    retrieval_k: int = int(os.getenv("RETRIEVAL_K", "10"))

    # Logging Settings
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)





def configure_logging() -> None:
    """Configure root logger for the application."""
    settings = get_settings()

    # Create logger format
    log_format = (
        "[%(asctime)s] - [%(name)s] - [%(levelname)s] - "
        "[%(filename)s:%(lineno)d] - %(message)s"
    )

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # Console output
        ]
    )

    # Set logging level for specific modules if needed
    logging.getLogger("uvicorn").setLevel(logging.INFO)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
