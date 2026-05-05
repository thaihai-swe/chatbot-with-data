from __future__ import annotations

from pathlib import Path
from typing import Any

from extractors.common import normalized_text_hash, sha256_bytes, title_from_filename


class TextExtractor:
    def extract(self, artifact_path: str, source_type: str) -> dict[str, Any]:
        path = Path(artifact_path)
        content = path.read_bytes()
        last_error: UnicodeDecodeError | None = None
        encoding_used = "utf-8"
        for encoding in ("utf-8", "utf-16", "latin-1"):
            try:
                text = content.decode(encoding)
                encoding_used = encoding
                break
            except UnicodeDecodeError as exc:
                last_error = exc
        else:
            raise ValueError(f"Unable to decode text file: {last_error}")

        return {
            "title": title_from_filename(path),
            "source_uri": None,
            "canonical_source_uri": None,
            "mime_type": "text/markdown" if source_type == "md" else "text/plain",
            "extracted_text": text,
            "metadata": {
                "filename": path.name,
                "file_size": path.stat().st_size,
                "encoding": encoding_used,
            },
            "file_hash": sha256_bytes(content),
            "normalized_text_hash": normalized_text_hash(text),
            "snapshot_path": None,
        }
