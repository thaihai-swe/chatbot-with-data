from __future__ import annotations

import logging
from typing import List, Dict, Any

from providers.base import BaseLLMProvider
from chat.prompts import CONFLICT_DETECTION_EVALUATION_PROMPT
from chat.utils import parse_json_from_llm

logger = logging.getLogger(__name__)

from config import get_config

class ConflictDetectionService:
    """Service to post-process answers and detect contradictions between sources."""

    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm_provider = llm_provider
        # Load from safety config, default to 0.8
        config = get_config()
        self.conflict_score_threshold = config.safety.conflict_score_threshold

    def detect_conflict(self, answer_text: str, retrieved_chunks: List[Dict[str, Any]]) -> dict[str, Any]:
        """
        Evaluate if retrieved sources contain conflicts and if the answer surfaced them.

        Args:
            answer_text: Generated answer
            retrieved_chunks: Chunks used in generation

        Returns:
            Dict containing has_conflict, conflict_score, surfaced_correctly, conflict_details
        """
        if not answer_text or not retrieved_chunks:
            return {
                "has_conflict": False,
                "conflict_score": 0.0,
                "surfaced_correctly": True,
                "conflict_details": ""
            }

        # 1. Format the context text
        context_text = "\n\n".join([
            f"[Source {i+1}] (Doc: {c.get('title', 'Unknown')}): {c.get('text', '')}"
            for i, c in enumerate(retrieved_chunks)
        ])

        # 2. Format the prompt
        prompt = CONFLICT_DETECTION_EVALUATION_PROMPT.format(
            answer_text=answer_text,
            context_text=context_text
        )

        try:
            response = self.llm_provider.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            data = parse_json_from_llm(response)
            if isinstance(data, dict):
                conflict_score = float(data.get("conflict_score", 0.0))
                # Explicit fallback to 'has_conflict' if no score, else use threshold
                has_conflict = conflict_score >= self.conflict_score_threshold
                if "conflict_score" not in data and "has_conflict" in data:
                    has_conflict = bool(data.get("has_conflict"))

                return {
                    "has_conflict": has_conflict,
                    "conflict_score": conflict_score,
                    "surfaced_correctly": bool(data.get("surfaced_correctly", True)),
                    "conflict_details": str(data.get("conflict_details", ""))
                }
        except Exception as e:
            logger.error(f"Conflict detection LLM check failed: {str(e)}")

        return {
            "has_conflict": False,
            "conflict_score": 0.0,
            "surfaced_correctly": True,
            "conflict_details": "Conflict check failed due to system error."
        }
