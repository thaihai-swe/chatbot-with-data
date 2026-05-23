import sys
import json

# Add backend to path
sys.path.append('backend')

from backend.config import get_settings_manager
from backend.schemas.settings import GlobalSettings

sm = get_settings_manager()

# Simulate frontend GET -> PUT
current_json = json.loads(sm.config.model_dump_json())

# Try updating
try:
    sm.update(current_json)
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
