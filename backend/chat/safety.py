"""Service for safety and prompt-injection defense."""
from __future__ import annotations

import logging
import re
import json
from typing import List, Dict, Any, Optional

from fastapi import Depends
from config import get_settings, get_config
from llm.client import LLMClient, get_llm_client
from schemas.chat import SafetyTrace, SafetyGroundedness, SafetyAnswerability
from chat.prompts import SAFETY_CLASSIFICATION_PROMPT
from chat.utils import parse_json_from_llm

logger = logging.getLogger(__name__)


class SafetyService:
    """Service for query classification and prompt-injection detection."""

    # Common prompt-injection patterns
    INJECTION_PATTERNS = [
        r"(?i)ignore\s+previous\s+instructions",
        r"(?i)disregard\s+all\s+previous",
        r"(?i)reveal\s+your\s+system\s+prompt",
        r"(?i)system\s+instructions",
        r"(?i)you\s+are\s+now\s+a",
        r"(?i)new\s+rule:",
        r"(?i)instead\s+of\s+answering",
        r"(?i)do\s+not\s+cite\s+sources",
        r"(?i)disable\s+citations",
    ]

    def __init__(self, llm_client: LLMClient, safety_threshold: float = 0.7):
        self.llm_client = llm_client
        self.safety_threshold = safety_threshold

    def _check_heuristics(self, text: str) -> List[str]:
        """Check text against heuristic patterns."""
        matched = []
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, text):
                matched.append(pattern)
        return matched

    def check_query(self, query: str) -> SafetyTrace:
        """
        Check a user query for safety and classification.

        Args:
            query: User input query string.

        Returns:
            SafetyTrace containing classification and risk assessment.
        """
        # 1. Heuristic check
        matched_patterns = self._check_heuristics(query)
        heuristic_risk = "high" if matched_patterns else "low"

        # 2. LLM check
        prompt = SAFETY_CLASSIFICATION_PROMPT.format(query_text=query)
        messages = [{"role": "user", "content": prompt}]

        try:
            response_text = self.llm_client.generate_completion(messages)
            # Try to parse JSON from response using utility
            safety_data = parse_json_from_llm(response_text)
            
            if isinstance(safety_data, dict):
                classification = safety_data.get("classification", "safe")
                llm_risk_score = safety_data.get("risk_score", 0.0)
                reason = safety_data.get("reason", "LLM check completed.")
            else:
                logger.warning(f"Failed to parse safety LLM response: {response_text}")
                classification = "safe"
                llm_risk_score = 0.5 if matched_patterns else 0.0
                reason = "Failed to parse LLM response."
        except Exception as e:
            logger.error(f"Error in safety LLM call: {str(e)}")
            classification = "safe"
            llm_risk_score = 1.0 if matched_patterns else 0.0
            reason = f"Safety check failed: {str(e)}"

        # Combine risks
        final_risk = "high" if (heuristic_risk == "high" or llm_risk_score > self.safety_threshold or classification == "adversarial") else "low"

        return SafetyTrace(
            query_classification=classification,
            injection_risk=final_risk,
            matched_patterns=matched_patterns,
            classifier_reason=reason,
            groundedness=SafetyGroundedness(status="unchecked"),
            answerability=SafetyAnswerability(is_answerable=(final_risk == "low"))
        )

    def check_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check retrieved chunks for potential prompt-injection or safety risks.

        Args:
            chunks: List of retrieved chunks.

        Returns:
            List of chunks, with risk metadata added.
        """
        processed_chunks = []
        for chunk in chunks:
            chunk_text = chunk.get("text", "")
            matched_patterns = self._check_heuristics(chunk_text)

            # Add safety metadata to the chunk
            safe_chunk = chunk.copy()
            safe_chunk["safety_risk"] = "high" if matched_patterns else "low"
            safe_chunk["safety_matched_patterns"] = matched_patterns

            if matched_patterns:
                logger.warning(f"Malicious pattern detected in chunk {chunk.get('chunk_id')}: {matched_patterns}")

            processed_chunks.append(safe_chunk)

        return processed_chunks


def get_safety_service(llm_client: LLMClient = Depends(get_llm_client)) -> SafetyService:
    """Factory function for SafetyService."""
    config = get_config()
    return SafetyService(llm_client, safety_threshold=config.safety.injection_risk_threshold)
