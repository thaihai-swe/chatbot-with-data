from __future__ import annotations

import pytest

from chunking.semantic_chunker import SemanticChunker


class MockProvider:
    def __init__(self, vectors=None):
        self.vectors = vectors

    def embed_batch(self, texts):
        if self.vectors:
            return self.vectors[:len(texts)]
        return [[0.1, 0.2, 0.3]] * len(texts)


class TestSemanticChunker:
    """Unit tests for SemanticChunker (AC-006 / REQ-005 / NFR-001)."""

    def test_no_embedding_provider(self):
        s = SemanticChunker(512, embedding_provider=None)
        chunks = s.chunk("Some text. Different topic now. Back to original.")
        assert len(chunks) >= 1
        assert not s.fallback_applied

    def test_with_mock_embedding_provider(self):
        s = SemanticChunker(512, embedding_provider=MockProvider())
        chunks = s.chunk("Topic one. Still topic one. Totally different now.")
        assert len(chunks) >= 1

    def test_provider_timeout_fallback_to_jaccard(self):
        class SlowProvider:
            def embed_batch(self, texts):
                import time
                time.sleep(6)
                return [[0.1] * 3] * len(texts)

        s = SemanticChunker(512, embedding_provider=SlowProvider(), embedding_timeout=5.0)
        chunks = s.chunk("First. Second. Third.")
        assert len(chunks) >= 1

    def test_provider_failure_fallback_to_jaccard(self):
        class FailingProvider:
            def embed_batch(self, texts):
                raise RuntimeError("provider unavailable")

        s = SemanticChunker(512, embedding_provider=FailingProvider())
        chunks = s.chunk("Word one. Word two. Word three.")
        assert len(chunks) >= 1

    def test_weak_segmentation_fallback_to_fixed(self):
        s = SemanticChunker(512, embedding_provider=None)
        chunks = s.chunk("A. B. C. D. E. F.")
        parents = [c for c in chunks if c.metadata.get("parent_chunk")]
        assert len(chunks) >= 1
        weak = s._is_weak_segmentation([0.5, 0.51, 0.49, 0.52, 0.5])
        assert weak is True

    def test_strong_segmentation_no_fallback(self):
        s = SemanticChunker(512, embedding_provider=None)
        strong = s._is_weak_segmentation([0.1, 0.9, 0.2, 0.8, 0.15])
        assert strong is False

    def test_empty_text(self):
        s = SemanticChunker(512)
        assert s.chunk("") == []
        assert s.chunk("   ") == []

    def test_cosine_similarity_identical(self):
        from chunking.semantic_chunker import _cosine_similarity
        sim = _cosine_similarity([1.0, 0.0], [1.0, 0.0])
        assert abs(sim - 1.0) < 0.001

    def test_cosine_similarity_orthogonal(self):
        from chunking.semantic_chunker import _cosine_similarity
        sim = _cosine_similarity([1.0, 0.0], [0.0, 1.0])
        assert abs(sim) < 0.001

    def test_embedding_scores_via_provider(self):
        vectors = [[0.1, 0.2], [0.1, 0.2], [0.9, 0.8]]
        s = SemanticChunker(512, embedding_provider=MockProvider(vectors=vectors))
        scores = s._calculate_embedding_scores(["A", "B", "C"])
        assert scores is not None
        assert len(scores) == 3
        assert abs(scores[1] - 1.0) < 0.001  # first pair identical
