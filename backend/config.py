from __future__ import annotations

import logging
import os
import json
import shutil
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from dotenv import load_dotenv
from schemas.settings import GlobalSettings

load_dotenv()

def get_env_path(name: str, default: str) -> Path:
    return Path(os.getenv(name, default))

@dataclass(frozen=True)
class Settings:
    """Legacy settings for backward compatibility during Phase 2."""
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "Knowledge Ingestion API"))
    environment: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    data_dir: Path = field(default_factory=lambda: get_env_path("DATA_DIR", "data/knowledge_ingestion"))
    database_path: Path = field(default_factory=lambda: get_env_path("DATABASE_PATH", "data/knowledge_ingestion/app.db"))
    uploads_dir: Path = field(default_factory=lambda: get_env_path("UPLOADS_DIR", "data/knowledge_ingestion/uploads"))
    snapshots_dir: Path = field(default_factory=lambda: get_env_path("SNAPSHOTS_DIR", "data/knowledge_ingestion/snapshots"))
    run_artifacts_dir: Path = field(default_factory=lambda: get_env_path("RUN_ARTIFACTS_DIR", "data/knowledge_ingestion/runs"))
    settings_file: Path = field(default_factory=lambda: get_env_path("SETTINGS_FILE", "data/knowledge_ingestion/settings.json"))
    
    cors_origins: tuple[str, ...] = field(default_factory=lambda: tuple(
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ))
    request_id_header: str = "X-Request-ID"
    url_timeout_seconds: int = field(default_factory=lambda: int(os.getenv("URL_TIMEOUT_SECONDS", "10")))

    # LLM Settings
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_api_base: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_BASE"))
    chat_model: str = field(default_factory=lambda: os.getenv("CHAT_MODEL", "gpt-4o"))
    embedding_model: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))

    # Chroma Settings
    chroma_db_path: str = field(default_factory=lambda: os.getenv("CHROMA_DB_PATH", "data/.chroma_db"))
    chroma_collection_name: str = field(default_factory=lambda: os.getenv("CHROMA_COLLECTION_NAME", "document-chunks"))

    # RAG Settings
    context_window_size: int = field(default_factory=lambda: int(os.getenv("CONTEXT_WINDOW_SIZE", "128000")))
    max_history_turns: int = field(default_factory=lambda: int(os.getenv("MAX_HISTORY_TURNS", "10")))
    retrieval_k: int = field(default_factory=lambda: int(os.getenv("RETRIEVAL_K", "10")))
    min_similarity_threshold: float = field(default_factory=lambda: float(os.getenv("MIN_SIMILARITY_THRESHOLD", "0.1")))
    min_results_count: int = field(default_factory=lambda: int(os.getenv("MIN_RESULTS_COUNT", "1")))
    safety_risk_threshold: float = field(default_factory=lambda: float(os.getenv("SAFETY_RISK_THRESHOLD", "0.7")))

    # Logging Settings
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.run_artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)

class SettingsManager:
    def __init__(self):
        self.legacy_settings = Settings()
        self.legacy_settings.ensure_directories()
        self._config: Optional[GlobalSettings] = None
        self.load()

    def load(self):
        """Load settings from JSON, merged with environment defaults."""
        config_data = {}
        if self.legacy_settings.settings_file.exists():
            try:
                with open(self.legacy_settings.settings_file, "r") as f:
                    config_data = json.load(f)
            except Exception as e:
                logging.error(f"Failed to load settings from {self.legacy_settings.settings_file}: {e}")
        
        self._config = GlobalSettings(**config_data)

    @property
    def config(self) -> GlobalSettings:
        if self._config is None:
            self.load()
        return self._config

    def update(self, new_settings: Dict[str, Any]):
        """Validate and persist new settings. Handles one level of nesting."""
        current_data = self.config.model_dump()
        
        # Simple merge for top-level keys (ingestion, retrieval, etc.)
        for key, value in new_settings.items():
            if key in current_data and isinstance(value, dict) and isinstance(current_data[key], dict):
                current_data[key].update(value)
            else:
                current_data[key] = value
                
        updated_config = GlobalSettings(**current_data)
        
        # Atomic write
        temp_file = self.legacy_settings.settings_file.with_suffix(".tmp")
        with open(temp_file, "w") as f:
            json.dump(updated_config.model_dump(), f, indent=4)
        shutil.move(temp_file, self.legacy_settings.settings_file)
        
        self._config = updated_config

    def save_run_snapshot(self, run_id: str, domain: str = "chat") -> str:
        """Save a snapshot of effective config (secrets excluded)."""
        snapshot = self.config.model_dump()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"run_{domain}_{timestamp}_{run_id}.json"
        filepath = self.legacy_settings.run_artifacts_dir / filename
        
        with open(filepath, "w") as f:
            json.dump(snapshot, f, indent=4)
        
        return str(filepath)

@lru_cache()
def get_settings_manager() -> SettingsManager:
    return SettingsManager()

def get_settings() -> Settings:
    """Legacy accessor."""
    return get_settings_manager().legacy_settings

def get_config() -> GlobalSettings:
    """New accessor for hierarchical settings."""
    return get_settings_manager().config

def configure_logging() -> None:
    """Configure root logger for the application."""
    settings = get_settings()

    log_format = (
        "[%(asctime)s] - [%(name)s] - [%(levelname)s] - "
        "[%(filename)s:%(lineno)d] - %(message)s"
    )

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(),
        ]
    )

    logging.getLogger("uvicorn").setLevel(logging.INFO)
