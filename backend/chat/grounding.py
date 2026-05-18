"""Service for checking grounding and evidence quality."""
from __future__ import annotations

import logging
from typing import List, Dict, Any, Tuple

from config import get_settings, get_config
from llm.client import LLMClient, get_llm_client
from chat.prompts import GROUNDEDNESS_EVALUATION_PROMPT
from chat.utils import parse_json_from_llm
from fastapi import Depends

logger = logging.getLogger(__name__)


class GroundingService:
    """Service for evaluating evidence quality and groundedness."""

    def __init__(
        self,
        llm_client: LLMClient,
        min_similarity_threshold: float = -0.2,
        min_results_count: int = 1,
    ):
        """
        Initialize the grounding service.

        Args:
            llm_client: Client for LLM evaluation
            min_similarity_threshold: Minimum similarity score to consider evidence relevant
            min_results_count: Minimum number of results needed to attempt an answer
        """
        self.llm_client = llm_client
        self.min_similarity_threshold = min_similarity_threshold
        self.min_results_count = min_results_count

    def evaluate_evidence(
        self,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Tuple[bool, str]:
        """
        Evaluate if retrieved evidence is sufficient for an answer.

        Args:
            retrieved_chunks: List of retrieved chunks with similarity scores

        Returns:
            Tuple of (is_sufficient, refusal_reason)
        """
        if not retrieved_chunks or len(retrieved_chunks) < self.min_results_count:
            return False, "I couldn't find any relevant documents in the selected collection to answer your question."

        max_similarity = max(chunk.get('similarity_score', 0) for chunk in retrieved_chunks)

        if max_similarity < self.min_similarity_threshold:
            logger.info(f"Refusing answer due to low similarity: {max_similarity:.2f} < {self.min_similarity_threshold}")
            return False, (
                f"I found some potential matches, but they don't seem closely "
                f"related to your question (max similarity: {max_similarity:.2f}). "
                "I don't have enough confident information to provide an answer."
            )

        return True, ""

    def calculate_groundedness(
        self,
        answer_text: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Tuple[float, str]:
        """
        Calculate a groundedness score using LLM-as-a-judge.

        Returns:
            Tuple of (score, reason)
        """
        if not answer_text or not retrieved_chunks:
            return 0.0, "Missing answer or context."

        context_text = "\n\n".join([
            f"[Source {i+1}]: {c.get('text', '')}" 
            for i, c in enumerate(retrieved_chunks)
        ])

        prompt = GROUNDEDNESS_EVALUATION_PROMPT.format(
            answer_text=answer_text,
            context_text=context_text
        )

        try:
            response = self.llm_client.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            data = parse_json_from_llm(response)
            if isinstance(data, dict):
                score = float(data.get("score", 0.0))
                reason = data.get("reason", "No reason provided.")
                return score, reason
        except Exception as e:
            logger.error(f"Groundedness check failed: {str(e)}")
            
        return 0.0, "Evaluation failed due to system error."


def get_grounding_service(llm_client: LLMClient = Depends(get_llm_client)) -> GroundingService:
    """Factory function for GroundingService."""
    config = get_config()
    return GroundingService(
        llm_client=llm_client,
        min_similarity_threshold=config.safety.min_similarity_threshold,
        min_results_count=config.safety.min_results_count,
    )
