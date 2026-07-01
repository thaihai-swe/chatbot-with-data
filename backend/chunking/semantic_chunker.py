from __future__ import annotations

import math
import re
import time
from typing import Optional

from chunking.base import BaseChunker, ChunkData
from chunking.fixed_size_chunker import FixedSizeChunker


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(av * bv for av, bv in zip(a, b))
    na = math.sqrt(sum(av * av for av in a))
    nb = math.sqrt(sum(bv * bv for bv in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class SemanticChunker(BaseChunker):
    """Chunking strategy using semantic similarity to determine chunk boundaries."""

    def __init__(
        self,
        chunk_size: int = 512,
        overlap: int = 0,
        semantic_threshold: float = 0.5,
        embedding_provider: object | None = None,
        embedding_timeout: float = 5.0,
        fallback_on_weak: bool = True,
    ):
        super().__init__(chunk_size=chunk_size, overlap=overlap)
        self.semantic_threshold = max(0.0, min(1.0, semantic_threshold))
        self.embedding_provider = embedding_provider
        self.embedding_timeout = embedding_timeout
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
        if not text or not text.strip():
            return []

        metadata = metadata or {}

        sentences = self._split_into_sentences(text)

        if not sentences:
            return []

        semantic_scores = self._calculate_semantic_scores(sentences)

        if not semantic_scores or self._is_weak_segmentation(semantic_scores):
            self.fallback_applied = True
            if self.fallback_on_weak:
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
                return self._chunks_from_sentences(
                    sentences, title, page_number, source_url,
                    {**metadata, "fallback_applied": True, "semantic_score": 0.0}
                )

        chunk_groups = self._group_by_semantic_boundaries(sentences, semantic_scores)
        chunks = []

        for i, group in enumerate(chunk_groups, 1):
            chunk_text = " ".join(group)
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

    def _calculate_semantic_scores(self, sentences: list[str]) -> list[float]:
        if len(sentences) < 2:
            return [1.0] * len(sentences)

        # Try embedding-based scores when provider is available
        if self.embedding_provider is not None:
            embedding_scores = self._calculate_embedding_scores(sentences)
            if embedding_scores is not None:
                return embedding_scores

        # Fall back to Jaccard heuristic
        scores = [1.0]
        for i in range(1, len(sentences)):
            score = self._calculate_jaccard_similarity(sentences[i - 1], sentences[i])
            scores.append(score)
        return scores

    def _calculate_embedding_scores(self, sentences: list[str]) -> list[float] | None:
        """Compute cosine similarity between adjacent sentences via embedding provider.
        Returns None if the provider fails or times out (triggers Jaccard fallback)."""
        try:
            start = time.monotonic()
            embeddings = self.embedding_provider.embed_batch(sentences)
            elapsed = time.monotonic() - start
            if elapsed > self.embedding_timeout:
                return None
        except Exception:
            return None

        scores = [1.0]
        for i in range(1, len(embeddings)):
            sim = _cosine_similarity(embeddings[i - 1], embeddings[i])
            scores.append(max(0.0, min(1.0, sim)))
        return scores

    def _calculate_jaccard_similarity(self, sent1: str, sent2: str) -> float:
        words1 = set(sent1.lower().split())
        words2 = set(sent2.lower().split())

        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "is", "are", "was", "were"}
        words1 -= stop_words
        words2 -= stop_words

        if not words1 or not words2:
            return 0.5

        intersection = len(words1 & words2)
        union = len(words1 | words2)
        similarity = intersection / union if union > 0 else 0.0

        len_ratio = min(len(sent1), len(sent2)) / max(len(sent1), len(sent2))
        return (similarity * 0.6 + len_ratio * 0.4)

    def _is_weak_segmentation(self, semantic_scores: list[float]) -> bool:
        if not semantic_scores:
            return True
        avg_score = sum(semantic_scores) / len(semantic_scores)
        variance = sum((s - avg_score) ** 2 for s in semantic_scores) / len(semantic_scores)
        return variance < 0.05

    def _group_by_semantic_boundaries(
        self,
        sentences: list[str],
        semantic_scores: list[float]
    ) -> list[list[str]]:
        if not sentences:
            return []

        groups = [[sentences[0]]]
        current_size = self.estimate_tokens(sentences[0])

        for i in range(1, len(sentences)):
            sentence = sentences[i]
            sentence_tokens = self.estimate_tokens(sentence)

            if current_size + sentence_tokens > self.chunk_size:
                if semantic_scores[i] < self.semantic_threshold:
                    groups.append([sentence])
                    current_size = sentence_tokens
                else:
                    groups[-1].append(sentence)
                    current_size += sentence_tokens
            else:
                groups[-1].append(sentence)
                current_size += sentence_tokens

        return groups

    def _split_into_sentences(self, text: str) -> list[str]:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _chunks_from_sentences(
        self,
        sentences: list[str],
        title: str | None,
        page_number: int | None,
        source_url: str | None,
        metadata: dict,
    ) -> list[ChunkData]:
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
