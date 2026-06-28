"""Service for document understanding via LLM analysis."""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

from chat.prompts import DOCUMENT_UNDERSTANDING_PROMPT
from providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class DocumentUnderstandingService:
    """Analyzes documents to extract summary, topics, and section hierarchy."""

    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm_provider = llm_provider

    def understand(self, text: str, title: Optional[str] = None) -> Optional[dict[str, Any]]:
        """Analyze a document and return structured understanding.

        Args:
            text: Full document text
            title: Optional document title

        Returns:
            Dict with keys 'summary', 'topics', 'sections' or None on failure.
        """
        prompt = DOCUMENT_UNDERSTANDING_PROMPT.format(
            title=title or "Untitled",
            document_text=text,
        )

        try:
            response = self.llm_provider.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
        except Exception as e:
            logger.warning(f"Document understanding LLM call failed: {e}")
            return None

        result = self._parse_response(response)
        if result is None:
            logger.warning("Document understanding failed to parse LLM response")
        return result

    def _parse_response(self, response: str) -> Optional[dict[str, Any]]:
        """Parse LLM JSON response into structured dict."""
        cleaned = response.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if len(lines) >= 3:
                cleaned = "\n".join(lines[1:-1])

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            return None

        if not isinstance(data, dict):
            return None

        return {
            "summary": data.get("summary", ""),
            "topics": data.get("topics", []),
            "sections": data.get("sections", []),
        }
