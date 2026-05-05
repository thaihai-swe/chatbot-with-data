from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from fastapi import UploadFile

from config import get_settings


class LocalStorage:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def save_upload(self, upload_file: UploadFile) -> tuple[str, str]:
        suffix = Path(upload_file.filename or "upload.bin").suffix
        file_id = f"{uuid.uuid4()}{suffix}"
        destination = self.settings.uploads_dir / file_id
        content = await upload_file.read()
        destination.write_bytes(content)
        return str(destination), hashlib.sha256(content).hexdigest()

    def save_snapshot(self, *, content: str, suffix: str = ".html") -> str:
        snapshot_path = self.settings.snapshots_dir / f"{uuid.uuid4()}{suffix}"
        snapshot_path.write_text(content, encoding="utf-8")
        return str(snapshot_path)
