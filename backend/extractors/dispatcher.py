from __future__ import annotations

from typing import Any

from extractors.pdf_extractor import PdfExtractor
from extractors.text_extractor import TextExtractor
from extractors.web_extractor import WebExtractor
from models import SourceType


class ExtractorDispatcher:
    def __init__(self) -> None:
        self.pdf_extractor = PdfExtractor()
        self.text_extractor = TextExtractor()
        self.web_extractor = WebExtractor()

    def extract(
        self,
        *,
        source_type: str,
        artifact_path: str | None = None,
        source_uri: str | None = None,
        fallback_title: str | None = None,
    ) -> dict[str, Any]:
        if source_type == SourceType.PDF.value:
            if not artifact_path:
                raise ValueError("PDF ingestion requires an artifact path")
            return self.pdf_extractor.extract(artifact_path, fallback_title=fallback_title)
        if source_type in {SourceType.TEXT.value, SourceType.MARKDOWN.value}:
            if not artifact_path:
                raise ValueError("Text ingestion requires an artifact path")
            return self.text_extractor.extract(
                artifact_path, source_type, fallback_title=fallback_title
            )
        if source_type == SourceType.URL.value:
            if not source_uri:
                raise ValueError("URL ingestion requires a source URI")
            return self.web_extractor.extract(source_uri, fallback_title=fallback_title)
        raise ValueError(f"Unsupported source type: {source_type}")
