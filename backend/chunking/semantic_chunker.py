from __future__ import annotations

import re
import hashlib
from typing import Optional

from chunking.base import BaseChunker, ChunkData
from chunking.fixed_size_chunker import FixedSizeChunker


class SemanticChunker(BaseChunker):
    """Chunking strategy using semantic similarity to determine chunk boundaries."""

    def __init__(
        self,
        chunk_size: int = 512,
        overlap: int = 0,
        semantic_threshold: float = 0.5,
        use_embeddings: bool = False,
        fallback_on_weak: bool = True,
    ):
        """
        Initialize semantic chunker.

        Args:
            chunk_size: Target size for chunks in tokens
            overlap: Overlap between chunks
            semantic_threshold: Threshold for semantic boundaries (0.0-1.0).
                               Lower = more aggressive splitting
            use_embeddings: Whether to use OpenAI embeddings for similarity
                           (deferred for now; use simple heuristics)
            fallback_on_weak: If True, fall back to fixed-size if semantic
                            detection is weak
        """
        super().__init__(chunk_size=chunk_size, overlap=overlap)
        self.semantic_threshold = max(0.0, min(1.0, semantic_threshold))
        self.use_embeddings = use_embeddings
        self.fallback_on_weak = fallback_on_weak
        self.fallback_applied = False

    def chunk(
        self,
        text: str,
        *,
        source_type: str = "text",
        title: str | None = None,
        page_number: int | None = None,
        source_url: str | None = None,
        metadata: dict | None = None,
    ) -> list[ChunkData]:
        """
        Create semantic chunks based on topic/content boundaries.

        Uses sentence-level analysis with simple heuristics:
        - Long gaps between sentences suggest topic change
        - Repeated keywords suggest continuation
        - Fallback to fixed-size if weak semantic signal
        """
        if not text or not text.strip():
            return []

        metadata = metadata or {}

        # Split into sentences
        sentences = self._split_into_sentences(text)

        if not sentences:
            return []

        # Try to identify semantic boundaries
        semantic_scores = self._calculate_semantic_scores(sentences)

        # Check if semantic segmentation is strong enough
        if not semantic_scores or self._is_weak_segmentation(semantic_scores):
            self.fallback_applied = True
            if self.fallback_on_weak:
                # Fall back to fixed-size chunking
                fixed_chunker = FixedSizeChunker(
                    chunk_size=self.chunk_size,
                    overlap=self.overlap
                )

                fallback_chunks = fixed_chunker.chunk(
                    text,
                    source_type=source_type,
                    title=title,
                    page_number=page_number,
                    source_url=source_url,
                    metadata={**metadata, "fallback_applied": True, "fallback_reason": "weak_semantic_signal"}
                )
                return fallback_chunks
            else:
                # Use sentences as chunks even with weak signal
                return self._chunks_from_sentences(
                    sentences, title, page_number, source_url,
                    {**metadata, "fallback_applied": True, "semantic_score": 0.0}
                )

        # Create chunks based on semantic boundaries
        chunk_groups = self._group_by_semantic_boundaries(sentences, semantic_scores)
        chunks = []

        for i, group in enumerate(chunk_groups, 1):
            chunk_text = " ".join(group)

            # Calculate semantic score for this chunk
            chunk_semantic_score = sum(
                semantic_scores[sentences.index(s)] for s in group if s in sentences
            ) / len(group) if group else 0.0

            chunk = ChunkData(
                chunk_order=i,
                text=chunk_text,
                title=title,
                page_number=page_number,
                source_url=source_url,
                fallback_applied=False,
                semantic_score=chunk_semantic_score,
                metadata={
                    **metadata,
                    "strategy": "semantic",
                    "semantic_score": chunk_semantic_score,
                    "sentence_count": len(group),
                }
            )

            chunks.append(chunk)

        return chunks

    def _split_into_sentences(self, text: str) -> list[str]:
        """Split text into sentences using regex."""
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        # Filter empty sentences and normalize whitespace
        return [s.strip() for s in sentences if s.strip()]

    def _calculate_semantic_scores(self, sentences: list[str]) -> list[float]:
        """
        Calculate semantic continuity scores for each sentence.

        Simple heuristic-based approach:
        - Compare sentence length consistency
        - Check for repeated keywords
        - Look for structural markers

        Returns: List of scores (0.0-1.0) where higher = stronger semantic continuity
        """
        if len(sentences) < 2:
            return [1.0] * len(sentences)

        scores = []

        for i, sentence in enumerate(sentences):
            if i == 0:
                scores.append(1.0)  # First sentence always high
                continue

            prev_sentence = sentences[i - 1]

            # Calculate similarity heuristics
            score = self._calculate_sentence_similarity(prev_sentence, sentence)
            scores.append(score)

        return scores

    def _calculate_sentence_similarity(self, sent1: str, sent2: str) -> float:
        """Calculate similarity between two sentences (0.0-1.0)."""
        words1 = set(sent1.lower().split())
        words2 = set(sent2.lower().split())

        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "is", "are", "was", "were"}
        words1 -= stop_words
        words2 -= stop_words

        if not words1 or not words2:
            return 0.5  # Neutral score for very short sentences

        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        similarity = intersection / union if union > 0 else 0.0

        # Length consistency bonus (similar length = higher score)
        len_ratio = min(len(sent1), len(sent2)) / max(len(sent1), len(sent2))

        return (similarity * 0.6 + len_ratio * 0.4)

    def _is_weak_segmentation(self, semantic_scores: list[float]) -> bool:
        """Determine if semantic segmentation signal is too weak."""
        if not semantic_scores:
            return True

        # If most sentences have very similar scores, signal is weak
        avg_score = sum(semantic_scores) / len(semantic_scores)
        variance = sum((s - avg_score) ** 2 for s in semantic_scores) / len(semantic_scores)

        # Low variance means weak differentiation between boundaries
        return variance < 0.05

    def _group_by_semantic_boundaries(
        self,
        sentences: list[str],
        semantic_scores: list[float]
    ) -> list[list[str]]:
        """Group sentences into chunks based on semantic boundaries."""
        if not sentences:
            return []

        groups = [[sentences[0]]]
        current_size = self.estimate_tokens(sentences[0])

        for i in range(1, len(sentences)):
            sentence = sentences[i]
            sentence_tokens = self.estimate_tokens(sentence)

            # Check if adding this sentence would exceed chunk size
            if current_size + sentence_tokens > self.chunk_size:
                # Check if there's a semantic boundary
                if semantic_scores[i] < self.semantic_threshold:
                    # Start new chunk
                    groups.append([sentence])
                    current_size = sentence_tokens
                else:
                    # Add to current chunk despite size
                    groups[-1].append(sentence)
                    current_size += sentence_tokens
            else:
                # Add to current chunk
                groups[-1].append(sentence)
                current_size += sentence_tokens

        return groups

    def _chunks_from_sentences(
        self,
        sentences: list[str],
        title: str | None,
        page_number: int | None,
        source_url: str | None,
        metadata: dict,
    ) -> list[ChunkData]:
        """Create chunks from sentence groups without semantic analysis."""
        chunks = []

        for i, sentence in enumerate(sentences, 1):
            chunk = ChunkData(
                chunk_order=i,
                text=sentence,
                title=title,
                page_number=page_number,
                source_url=source_url,
                metadata=metadata
            )
            chunks.append(chunk)

        return chunks
