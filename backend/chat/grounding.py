"""Service for checking grounding and evidence quality."""
from __future__ import annotations

import logging
import re
from typing import List, Dict, Any, Tuple

from config import get_settings, get_config
from providers.base import BaseLLMProvider
from providers.factory import get_llm_provider
from chat.prompts import GROUNDEDNESS_EVALUATION_PROMPT
from chat.utils import parse_json_from_llm
from fastapi import Depends

logger = logging.getLogger(__name__)

_SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+')


class GroundingService:
    """Service for evaluating evidence quality and groundedness."""

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        min_similarity_threshold: float = -0.2,
        min_results_count: int = 1,
        jaccard_top_k: int = 3,
        jaccard_min_overlap: float = 0.1,
    ):
        """
        Initialize the grounding service.

        Args:
            llm_provider: Provider for LLM evaluation
            min_similarity_threshold: Minimum similarity score to consider evidence relevant
            min_results_count: Minimum number of results needed to attempt an answer
            jaccard_top_k: Number of top chunks to keep after Jaccard filtering
            jaccard_min_overlap: Minimum Jaccard overlap to keep a chunk
        """
        self.llm_provider = llm_provider
        self.min_similarity_threshold = min_similarity_threshold
        self.min_results_count = min_results_count
        self.jaccard_top_k = jaccard_top_k
        self.jaccard_min_overlap = jaccard_min_overlap

        # Load config defaults from settings
        config = get_config()
        self.jaccard_top_k = config.safety.grounding_jaccard_top_k
        self.jaccard_min_overlap = config.safety.grounding_jaccard_min_overlap

    def _jaccard_top_k(
        self,
        answer_text: str,
        chunks: List[Dict[str, Any]],
        k: int = 3,
        min_overlap: float = 0.1,
    ) -> List[Dict[str, Any]]:
        """
        Compute word-overlap Jaccard score between answer sentences and each chunk.
        Returns top-K chunks with highest overlap >= min_overlap.

        Args:
            answer_text: The generated answer text
            chunks: List of retrieved chunks with 'text' or 'content' field
            k: Number of top chunks to return
            min_overlap: Minimum Jaccard overlap threshold

        Returns:
            List of top-K chunks with highest Jaccard overlap
        """
        if not answer_text or not chunks:
            return []

        # Split answer into sentences
        answer_sentences = _SENTENCE_SPLIT_RE.split(answer_text)
        answer_words = set(answer_text.lower().split())

        chunk_scores = []
        for chunk in chunks:
            chunk_text = chunk.get('text') or chunk.get('content') or ''
            chunk_words = set(chunk_text.lower().split())

            if not chunk_words:
                continue

            # Compute Jaccard: |A ∩ B| / |A ∪ B|
            intersection = answer_words & chunk_words
            union = answer_words | chunk_words
            score = len(intersection) / len(union) if union else 0.0

            if score >= min_overlap:
                chunk_scores.append((score, chunk))

        # Sort by score descending and take top K
        chunk_scores.sort(key=lambda x: x[0], reverse=True)
        return [chunk for score, chunk in chunk_scores[:k]]

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
        Calculate a groundedness score using Jaccard pre-filter + LLM-as-a-judge.

        Returns:
            Tuple of (score, reason)
        """
        if not answer_text or not retrieved_chunks:
            return 0.0, "Missing answer or context."

        # Step 1: Jaccard filter - keep top-K chunks with highest overlap
        filtered_chunks = self._jaccard_top_k(
            answer_text,
            retrieved_chunks,
            k=self.jaccard_top_k,
            min_overlap=self.jaccard_min_overlap,
        )

        # Fallback to all chunks if filtering removes everything
        if not filtered_chunks:
            filtered_chunks = retrieved_chunks[:self.jaccard_top_k] if retrieved_chunks else []

        # Step 2: LLM judge on filtered chunks
        context_text = "\n\n".join([
            f"[Source {i+1}]: {c.get('text', '')}"
            for i, c in enumerate(filtered_chunks)
        ])

        # Record filtered chunk IDs for traceability (if caller provides trace)
        # Note: This is populated by the caller (advanced_retrieval.py) when trace is available

        prompt = GROUNDEDNESS_EVALUATION_PROMPT.format(
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
                score = float(data.get("score", 0.0))
                reason = data.get("reason", "No reason provided.")
                return score, reason
        except Exception as e:
            logger.error(f"Groundedness check failed: {str(e)}")

        return 0.0, "Evaluation failed due to system error."


def get_grounding_service(llm_provider: BaseLLMProvider = Depends(get_llm_provider)) -> GroundingService:
    """Factory function for GroundingService."""
    config = get_config()
    return GroundingService(
        llm_provider=llm_provider,
        min_similarity_threshold=config.safety.min_similarity_threshold,
        min_results_count=config.safety.min_results_count,
    )
