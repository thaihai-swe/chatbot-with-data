import os
import sys
from pathlib import Path

# Add backend to path so we can import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import get_settings, get_settings_manager
from schemas.settings import GlobalSettings, IngestionSettings, RetrievalSettings, LLMSettings, SafetySettings

def migrate():
    print("🚀 Starting configuration migration...")
    
    # Get current legacy settings (loaded from .env)
    legacy = get_settings()
    
    # Map legacy settings to new hierarchical structure
    new_config = GlobalSettings(
        ingestion=IngestionSettings(
            chunk_size=legacy.context_window_size, # Note: mapping might not be 1:1, but this is a start
            embedding_model=legacy.embedding_model,
            vector_db_collection=legacy.weaviate_collection_name
        ),
        retrieval=RetrievalSettings(
            top_k=legacy.retrieval_k
        ),
        llm=LLMSettings(
            model=legacy.chat_model
        ),
        safety=SafetySettings(
            injection_risk_threshold=legacy.safety_risk_threshold
        )
    )
    
    # Use manager to save it
    manager = get_settings_manager()
    print(f"📄 Saving initial configuration to {legacy.settings_file}...")
    
    # We update the manager's config and save
    manager.update(new_config.model_dump())
    
    print("✅ Migration complete!")

if __name__ == "__main__":
    migrate()
