from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from config import get_settings_manager
from schemas.settings import GlobalSettings
from pydantic import ValidationError

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("", response_model=GlobalSettings)
async def get_all_settings():
    """Get all behavioral settings."""
    return get_settings_manager().config

@router.put("")
async def update_settings(new_settings: Dict[str, Any]):
    """Update behavioral settings and persist to disk."""
    try:
        get_settings_manager().update(new_settings)
        return {"status": "success", "message": "Settings updated and persisted."}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")
