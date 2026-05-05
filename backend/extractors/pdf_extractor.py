from __future__ import annotations

from pathlib import Path
from typing import Any

import pdfplumber
from PyPDF2 import PdfReader

from extractors.common import normalized_text_hash, sha256_bytes, title_from_filename


class PdfExtractor:
    def extract(self, artifact_path: str) -> dict[str, Any]:
        path = Path(artifact_path)
        content = path.read_bytes()
        file_hash = sha256_bytes(content)
        metadata: dict[str, Any] = {"filename": path.name}
        try:
            reader = PdfReader(str(path))
            metadata["page_count"] = len(reader.pages)
            if reader.metadata:
                metadata["pdf_metadata"] = {
                    key.lstrip("/"): str(value) for key, value in reader.metadata.items()
                }
        except Exception as exc:
            raise ValueError(f"Unable to read PDF metadata: {exc}") from exc

        try:
            with pdfplumber.open(str(path)) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
        except Exception as exc:
            raise ValueError(f"Unable to extract PDF text: {exc}") from exc

        text = "\n".join(page for page in pages if page).strip()
        title = metadata.get("pdf_metadata", {}).get("Title") or title_from_filename(path)
        return {
            "title": title,
            "source_uri": None,
            "canonical_source_uri": None,
            "mime_type": "application/pdf",
            "extracted_text": text,
            "metadata": metadata,
            "file_hash": file_hash,
            "normalized_text_hash": normalized_text_hash(text) if text else None,
            "snapshot_path": None,
        }
