import json
import re
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

def parse_json_from_llm(text: Any) -> Any:
    """Robustly parse JSON from LLM output, handling markdown blocks and conversational noise."""
    if not text or not isinstance(text, (str, bytes)):
        return None
    
    try:
        # Convert bytes to str if necessary
        content = text.decode("utf-8") if isinstance(text, bytes) else text
        content = content.strip()
        
        if not content:
            return None

        # 1. Handle potential surrounding quotes if the entire string is quoted
        if (content.startswith("'") and content.endswith("'")) or (content.startswith('"') and content.endswith('"')):
            content = content[1:-1].strip()

        # 2. Try direct parse first
        try:
            return json.loads(content)
        except (json.JSONDecodeError, ValueError):
            pass

        # 3. Try to find JSON block in markdown (```json ... ``` or ``` ... ```)
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except (json.JSONDecodeError, ValueError):
                pass

        # 4. Try to find anything that looks like a JSON array or object
        match = re.search(r"(\[.*\]|\{.*\})", content, re.DOTALL)
        if match:
            try:
                json_str = match.group(1).strip()
                return json.loads(json_str)
            except (json.JSONDecodeError, ValueError):
                pass

    except Exception as e:
        logger.debug(f"Unexpected error in parse_json_from_llm: {e}")
        
    return None
