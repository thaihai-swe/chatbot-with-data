import hashlib
import json
import uuid
from datetime import datetime, timezone


def utcnow_iso():
    return datetime.now(timezone.utc).isoformat()


def generate_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex}"


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def json_dumps(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True)
