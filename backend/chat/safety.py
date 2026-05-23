"""Service for safety and prompt-injection defense."""
from __future__ import annotations

import logging
import re
import json
import yaml
import math
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from fastapi import Depends
from config import get_settings, get_config
from providers.base import BaseLLMProvider, BaseEmbeddingProvider
from providers.factory import get_llm_provider, get_embedding_provider
from schemas.chat import SafetyTrace, SafetyGroundedness, SafetyAnswerability
from chat.prompts import SAFETY_CLASSIFICATION_PROMPT
from chat.utils import parse_json_from_llm

logger = logging.getLogger(__name__)


class HeuristicScanner:
    """Handles heuristic (regex-based) pattern matching for safety checks."""

    def __init__(self):
        self.patterns = self._load_patterns_from_yaml()

    def _validate_pattern(self, pattern_entry: Dict[str, Any], category: str) -> bool:
        """Validate a single pattern entry from YAML."""
        required_fields = ["pattern", "regex", "severity", "description"]

        for field in required_fields:
            if field not in pattern_entry:
                logger.warning(f"Pattern in category '{category}' missing required field '{field}'")
                return False

        regex = pattern_entry.get("regex")
        try:
            re.compile(regex)
        except re.error as e:
            logger.warning(f"Invalid regex in category '{category}': {regex} - {str(e)}")
            return False

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
            logger.warning("Returning empty pattern list since YAML failed to load")
            return []

    def scan(self, text: str) -> List[str]:
        """Check text against heuristic patterns and return matched ones."""
        matched = []
        for pattern in self.patterns:
            if re.search(pattern, text):
                matched.append(pattern)
        return matched


# Global cache for the injection corpus embeddings to avoid re-computing on every request
_GLOBAL_CORPUS_EMBEDDINGS: List[List[float]] = []
_CORPUS_LOADED: bool = False

class FuzzyScanner:
    """Handles semantic embedding-based fuzzy matching for safety checks."""

    def __init__(self, embedding_provider: BaseEmbeddingProvider):
        self.embedding_provider = embedding_provider
        self._embedding_cache: Dict[str, List[float]] = {}
        self._ensure_corpus_loaded()

    def _ensure_corpus_loaded(self):
        """Load and embed corpus only once globally."""
        global _GLOBAL_CORPUS_EMBEDDINGS, _CORPUS_LOADED
        if _CORPUS_LOADED:
            return

        corpus_path = Path(__file__).parent.parent / "config" / "injection_corpus.json"
        cache_path = Path(__file__).parent.parent / "config" / "injection_corpus_embeddings.json"
        
        try:
            # Check if we have a valid pre-computed cache file that is newer than the source corpus
            if cache_path.exists() and cache_path.stat().st_mtime > corpus_path.stat().st_mtime:
                with open(cache_path, "r") as f:
                    cache_data = json.load(f)
                _GLOBAL_CORPUS_EMBEDDINGS = cache_data.get("embeddings", [])
                logger.info(f"Loaded {len(_GLOBAL_CORPUS_EMBEDDINGS)} pre-computed injection corpus embeddings from disk cache.")
            else:
                with open(corpus_path, "r") as f:
                    corpus_data = json.load(f)
                corpus_examples = corpus_data.get("examples", [])
                
                # Pre-compute all embeddings for the corpus
                if corpus_examples:
                    logger.info(f"Pre-computing embeddings for {len(corpus_examples)} fuzzy injection examples...")
                    _GLOBAL_CORPUS_EMBEDDINGS = self.embedding_provider.embed_batch(corpus_examples)
                    
                    # Save to disk cache to avoid re-computation on next server restart
                    with open(cache_path, "w") as f:
                        json.dump({
                            "embeddings": _GLOBAL_CORPUS_EMBEDDINGS
                        }, f)
                    logger.info("Saved pre-computed embeddings to disk cache.")
            
            _CORPUS_LOADED = True
        except Exception as e:
            logger.error(f"Failed to load or embed injection corpus: {str(e)}")
            logger.info("Falling back to regex-only detection (no fuzzy matching)")

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using embedding provider with caching."""
        if text in self._embedding_cache:
            return self._embedding_cache[text]

        try:
            embedding = self.embedding_provider.embed(text)
            self._embedding_cache[text] = embedding
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            return []

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0

        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0.0 or magnitude2 == 0.0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def scan(self, text: str, similarity_threshold: float = 0.70) -> float:
        """Check query against injection corpus using fuzzy matching."""
        if not get_config().safety.fuzzy_matching_enabled:
            return 0.0

        if not _GLOBAL_CORPUS_EMBEDDINGS:
            return 0.0

        text_embedding = self._generate_embedding(text)
        if not text_embedding:
            return 0.0

        max_similarity = 0.0
        try:
            for example_embedding in _GLOBAL_CORPUS_EMBEDDINGS:
                similarity = self._cosine_similarity(text_embedding, example_embedding)
                if similarity > max_similarity:
                    max_similarity = similarity

                if similarity >= similarity_threshold:
                    logger.warning(f"Fuzzy match detected: text='{text}' matched an injection pattern (score={similarity:.3f})")
                    break
        except Exception as e:
            logger.error(f"Error during fuzzy similarity calculation: {str(e)}")
            return 0.0

        return max_similarity


class LLMScanner:
    """Handles LLM-based safety classification."""

    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm_provider = llm_provider

    def scan(self, text: str) -> Tuple[str, float, str]:
        """
        Evaluate text safety using the LLM.
        Returns: (classification, risk_score, reason)
        """
        prompt = SAFETY_CLASSIFICATION_PROMPT.format(query_text=text)
        messages = [{"role": "user", "content": prompt}]

        try:
            response_text = self.llm_provider.generate_completion(messages)
            safety_data = parse_json_from_llm(response_text)

            if isinstance(safety_data, dict):
                classification = safety_data.get("classification", "safe")
                risk_score = safety_data.get("risk_score", 0.0)
                reason = safety_data.get("reason", "LLM check completed.")
                return classification, risk_score, reason
            else:
                logger.warning(f"Failed to parse safety LLM response: {response_text}")
                return "safe", 0.0, "Failed to parse LLM response."
        except Exception as e:
            logger.error(f"Error in safety LLM call: {str(e)}")
            return "safe", 0.0, f"Safety check failed: {str(e)}"


class SafetyService:
    """Service for query classification and prompt-injection detection. Acts as Orchestrator."""

    def __init__(self, llm_provider: BaseLLMProvider, embedding_provider: BaseEmbeddingProvider, safety_threshold: float = 0.7):
        self.safety_threshold = safety_threshold
        self.heuristic_scanner = HeuristicScanner()
        self.fuzzy_scanner = FuzzyScanner(embedding_provider)
        self.llm_scanner = LLMScanner(llm_provider)

    def _get_threshold_for_mode(self, mode: str) -> float:
        """Get the risk threshold for a given safety mode."""
        threshold_map = {
            "strict": 0.5,
            "moderate": 0.7,
            "lenient": 0.9
        }
        return threshold_map.get(mode, 0.7)

    def check_query(self, query: str, safety_mode: str = "moderate") -> SafetyTrace:
        """Check a user query for safety and classification."""
        mode_threshold = self._get_threshold_for_mode(safety_mode)

        # 1. Heuristic check
        matched_patterns = self.heuristic_scanner.scan(query)
        heuristic_risk = "high" if matched_patterns else "low"

        # 2. Fuzzy detection check
        fuzzy_similarity = self.fuzzy_scanner.scan(query, similarity_threshold=0.70)
        fuzzy_risk = "high" if fuzzy_similarity >= 0.70 else "low"

        # 3. LLM check
        classification, llm_risk_score, reason = self.llm_scanner.scan(query)

        # Adjust LLM risk fallback if heuristics matched but LLM failed to catch it
        if matched_patterns and llm_risk_score == 0.0:
            llm_risk_score = 1.0

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
        """Check retrieved chunks for potential prompt-injection or safety risks."""
        processed_chunks = []
        for chunk in chunks:
            chunk_text = chunk.get("text", "")

            # 1. Heuristic pattern matching
            matched_patterns = self.heuristic_scanner.scan(chunk_text)

            # 2. Fuzzy detection
            fuzzy_similarity = self.fuzzy_scanner.scan(chunk_text, similarity_threshold=0.70)
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
