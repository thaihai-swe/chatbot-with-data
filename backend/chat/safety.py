"""Service for safety and prompt-injection defense."""
from __future__ import annotations

import logging
import re
import json
import yaml
import math
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import Depends
from config import get_settings, get_config
from providers.base import BaseLLMProvider, BaseEmbeddingProvider
from providers.factory import get_llm_provider, get_embedding_provider
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

    def __init__(self, llm_provider: BaseLLMProvider, embedding_provider: BaseEmbeddingProvider, safety_threshold: float = 0.7):
        self.llm_provider = llm_provider
        self.embedding_provider = embedding_provider
        self.safety_threshold = safety_threshold
        self.patterns = self._load_patterns_from_yaml()
        self._embedding_cache: Dict[str, List[float]] = {}

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using embedding provider with caching."""
        # Check cache first
        if text in self._embedding_cache:
            logger.debug(f"Embedding cache hit for text: {text[:50]}...")
            return self._embedding_cache[text]

        # Generate new embedding
        try:
            embedding = self.embedding_provider.embed(text)

            # Cache the result
            self._embedding_cache[text] = embedding
            logger.debug(f"Embedding cached for text: {text[:50]}...")

            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            return []

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0

        if len(vec1) != len(vec2):
            logger.warning(f"Vector dimension mismatch: {len(vec1)} vs {len(vec2)}")
            return 0.0

        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))

        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        # Avoid division by zero
        if magnitude1 == 0.0 or magnitude2 == 0.0:
            return 0.0

        # Calculate cosine similarity
        similarity = dot_product / (magnitude1 * magnitude2)

        return similarity

    def _check_fuzzy(self, query: str, similarity_threshold: float = 0.70) -> float:
        """
        Check query against injection corpus using fuzzy matching.

        Args:
            query: Query text to check
            similarity_threshold: Minimum similarity to consider a match

        Returns:
            Maximum similarity score found (0.0 to 1.0)
        """
        # Load corpus
        corpus_path = Path(__file__).parent.parent / "config" / "injection_corpus.json"
        try:
            with open(corpus_path, "r") as f:
                corpus_data = json.load(f)
            corpus_examples = corpus_data.get("examples", [])
        except Exception as e:
            logger.error(f"Failed to load injection corpus: {str(e)}")
            logger.info("Falling back to regex-only detection (no fuzzy matching)")
            return 0.0

        # Generate embedding for query
        query_embedding = self._generate_embedding(query)
        if not query_embedding:
            logger.warning("Failed to generate query embedding for fuzzy check")
            logger.info("Falling back to regex-only detection (no fuzzy matching)")
            return 0.0

        # Calculate similarity with each corpus example
        max_similarity = 0.0
        try:
            for example in corpus_examples:
                example_embedding = self._generate_embedding(example)
                if not example_embedding:
                    continue

                similarity = self._cosine_similarity(query_embedding, example_embedding)
                if similarity > max_similarity:
                    max_similarity = similarity

                # Early exit if we found a strong match
                if similarity >= similarity_threshold:
                    logger.warning(f"Fuzzy match detected: query='{query}' similar to '{example}' (score={similarity:.3f})")
                    break
        except Exception as e:
            logger.error(f"Error during fuzzy similarity calculation: {str(e)}")
            logger.info("Falling back to regex-only detection (no fuzzy matching)")
            return 0.0

        return max_similarity

    def _get_threshold_for_mode(self, mode: str) -> float:
        """Get the risk threshold for a given safety mode."""
        threshold_map = {
            "strict": 0.5,
            "moderate": 0.7,
            "lenient": 0.9
        }
        return threshold_map.get(mode, 0.7)

    def _validate_pattern(self, pattern_entry: Dict[str, Any], category: str) -> bool:
        """Validate a single pattern entry from YAML."""
        required_fields = ["pattern", "regex", "severity", "description"]

        # Check required fields
        for field in required_fields:
            if field not in pattern_entry:
                logger.warning(f"Pattern in category '{category}' missing required field '{field}'")
                return False

        # Validate regex
        regex = pattern_entry.get("regex")
        try:
            re.compile(regex)
        except re.error as e:
            logger.warning(f"Invalid regex in category '{category}': {regex} - {str(e)}")
            return False

        # Validate severity
        severity = pattern_entry.get("severity")
        if severity not in ["high", "medium", "low"]:
            logger.warning(f"Invalid severity '{severity}' in category '{category}'. Must be high, medium, or low")
            return False

        return True

    def _load_patterns_from_yaml(self) -> List[str]:
        """Load injection patterns from YAML configuration file."""
        config_path = Path(__file__).parent.parent / "config" / "injection_patterns.yaml"

        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)

            patterns = []
            injection_patterns = data.get("injection_patterns", {})

            for category, pattern_list in injection_patterns.items():
                for pattern_entry in pattern_list:
                    if self._validate_pattern(pattern_entry, category):
                        regex = pattern_entry.get("regex")
                        if regex:
                            patterns.append(regex)

            logger.info(f"Loaded {len(patterns)} injection patterns from YAML")
            return patterns

        except Exception as e:
            logger.error(f"Failed to load patterns from YAML: {str(e)}")
            logger.warning("Falling back to hardcoded INJECTION_PATTERNS")
            return self.INJECTION_PATTERNS

    def _check_heuristics(self, text: str) -> List[str]:
        """Check text against heuristic patterns."""
        matched = []
        for pattern in self.patterns:
            if re.search(pattern, text):
                matched.append(pattern)
        return matched

    def check_query(self, query: str, safety_mode: str = "moderate") -> SafetyTrace:
        """
        Check a user query for safety and classification.

        Args:
            query: User input query string.
            safety_mode: Safety mode (strict, moderate, lenient).

        Returns:
            SafetyTrace containing classification and risk assessment.
        """
        # Get threshold for the specified mode
        mode_threshold = self._get_threshold_for_mode(safety_mode)

        # 1. Heuristic check
        matched_patterns = self._check_heuristics(query)
        heuristic_risk = "high" if matched_patterns else "low"

        # 2. Fuzzy detection check
        fuzzy_similarity = self._check_fuzzy(query, similarity_threshold=0.70)
        fuzzy_risk = "high" if fuzzy_similarity >= 0.70 else "low"

        # 3. LLM check
        prompt = SAFETY_CLASSIFICATION_PROMPT.format(query_text=query)
        messages = [{"role": "user", "content": prompt}]

        try:
            response_text = self.llm_provider.generate_completion(messages)
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

        # Combine risks: heuristic, fuzzy, and LLM
        final_risk = "high" if (
            heuristic_risk == "high" or
            fuzzy_risk == "high" or
            llm_risk_score > mode_threshold or
            classification == "adversarial"
        ) else "low"

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

            # 1. Heuristic pattern matching
            matched_patterns = self._check_heuristics(chunk_text)

            # 2. Fuzzy detection
            fuzzy_similarity = self._check_fuzzy(chunk_text, similarity_threshold=0.70)
            fuzzy_risk = "high" if fuzzy_similarity >= 0.70 else "low"

            # Add safety metadata to the chunk
            safe_chunk = chunk.copy()
            safe_chunk["safety_risk"] = "high" if (matched_patterns or fuzzy_risk == "high") else "low"
            safe_chunk["safety_matched_patterns"] = matched_patterns
            safe_chunk["safety_fuzzy_similarity"] = fuzzy_similarity

            if matched_patterns:
                logger.warning(f"Malicious pattern detected in chunk {chunk.get('chunk_id')}: {matched_patterns}")

            if fuzzy_risk == "high":
                logger.warning(f"Fuzzy match detected in chunk {chunk.get('chunk_id')}: similarity={fuzzy_similarity:.3f}")

            processed_chunks.append(safe_chunk)

        return processed_chunks


def get_safety_service(
    llm_provider: BaseLLMProvider = Depends(get_llm_provider),
    embedding_provider: BaseEmbeddingProvider = Depends(get_embedding_provider)
) -> SafetyService:
    """Factory function for SafetyService."""
    config = get_config()
    return SafetyService(llm_provider, embedding_provider, safety_threshold=config.safety.injection_risk_threshold)
