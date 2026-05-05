from __future__ import annotations

import hashlib
import re
from pathlib import Path


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def normalize_text(value: str) -> str:
    collapsed = re.sub(r"\s+", " ", value).strip().lower()
    return collapsed


def normalized_text_hash(value: str) -> str:
    return sha256_bytes(normalize_text(value).encode("utf-8"))


def title_from_filename(path: str | Path) -> str:
    return Path(path).stem or "Untitled"
