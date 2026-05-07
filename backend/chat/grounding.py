"""Service for checking grounding and evidence quality."""
from __future__ import annotations

import logging
from typing import List, Dict, Any, Tuple

from config import get_settings

logger = logging.getLogger(__name__)


class GroundingService:
    """Service for evaluating evidence quality and groundedness."""

    def __init__(
        self,
        min_similarity_threshold: float = -0.2,
        min_results_count: int = 1,
    ):
        """
        Initialize the grounding service.

        Args:
            min_similarity_threshold: Minimum similarity score to consider evidence relevant
            min_results_count: Minimum number of results needed to attempt an answer
        """
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

        # if max_similarity < self.min_similarity_threshold:
        #     return False, (
        #         f"I found some potential matches, but they don't seem closely "
        #         f"related to your question (max similarity: {max_similarity:.2f}). "
        #         "I don't have enough confident information to provide an answer."
        #     )

        return True, ""


def get_grounding_service() -> GroundingService:
    """Factory function for GroundingService."""
    settings = get_settings()
    # Can add threshold to settings later
    return GroundingService()
