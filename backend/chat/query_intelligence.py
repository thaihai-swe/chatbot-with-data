from __future__ import annotations

import logging
import re
from typing import Dict, List, Tuple

from fastapi import Depends
from providers.base import BaseLLMProvider
from providers.factory import get_llm_provider
from chat.prompts import (
    QUERY_CLASSIFICATION_PROMPT,
    QUERY_EXPANSION_PROMPT,
    QUERY_REWRITING_PROMPT,
    QUERY_DECOMPOSITION_PROMPT,
    HYDE_PROMPT,
    SYNONYM_EXPANSION_PROMPT,
)
from chat.utils import parse_json_from_llm

logger = logging.getLogger(__name__)


class QueryIntelligenceService:
    """Service for LLM-powered query intelligence and transformation."""

    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm_provider = llm_provider

    def _call_llm(self, prompt: str) -> str:
        result = self.llm_provider.generate_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            stream=False,
        )
        if result:
            result = result.strip()
            result = re.sub(r"\(Note:.*?\)", "", result, flags=re.IGNORECASE | re.DOTALL).strip()
        return result

    def classify_query(self, query_text: str) -> Tuple[str, float]:
        prompt = QUERY_CLASSIFICATION_PROMPT.format(query_text=query_text)
        result = self._call_llm(prompt)
        parsed = parse_json_from_llm(result)
        if isinstance(parsed, dict):
            intent = parsed.get("intent", "factual")
            confidence = parsed.get("confidence_score", 0.0)
            try:
                confidence = float(confidence)
            except (ValueError, TypeError):
                confidence = 0.0
            return str(intent), confidence
        return "factual", 0.0

    def expand_query(self, query_text: str, count: int) -> List[str]:
        prompt = QUERY_EXPANSION_PROMPT.format(query_text=query_text, count=count)
        result = self._call_llm(prompt)
        parsed = parse_json_from_llm(result)
        if isinstance(parsed, list):
            return [str(q).strip() for q in parsed]
        logger.error(f"Failed to parse query expansion JSON: {result}")
        return []

    def rewrite_query(self, query_text: str) -> str:
        prompt = QUERY_REWRITING_PROMPT.format(query_text=query_text)
        return self._call_llm(prompt)

    def decompose_query(self, query_text: str) -> List[str]:
        prompt = QUERY_DECOMPOSITION_PROMPT.format(query_text=query_text)
        result = self._call_llm(prompt)
        parsed = parse_json_from_llm(result)
        if isinstance(parsed, list):
            return [str(q).strip() for q in parsed]
        logger.error(f"Failed to parse query decomposition JSON: {result}")
        return []

    def generate_hyde(self, query_text: str) -> str:
        prompt = HYDE_PROMPT.format(query_text=query_text)
        return self._call_llm(prompt)

    def expand_synonyms(self, query_text: str) -> Dict[str, str]:
        prompt = SYNONYM_EXPANSION_PROMPT.format(query_text=query_text)
        result = self._call_llm(prompt)
        parsed = parse_json_from_llm(result)
        if isinstance(parsed, dict):
            cleaned = {}
            for k, v in parsed.items():
                if isinstance(v, list):
                    cleaned[str(k)] = " ".join(map(str, v))
                else:
                    cleaned[str(k)] = str(v)
            return cleaned
        logger.error(f"Failed to parse synonym JSON: {result}")
        return {}


def get_query_intelligence_service(
    llm_provider: BaseLLMProvider = Depends(get_llm_provider),
) -> QueryIntelligenceService:
    return QueryIntelligenceService(llm_provider)
