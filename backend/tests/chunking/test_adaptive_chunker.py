from __future__ import annotations

import pytest

from chunking.base import ChunkData
from chunking.adaptive_chunker import AdaptiveChunker


class TestAdaptiveChunker:
    """Unit tests for AdaptiveChunker (AC-001)."""

    def test_inject_small_doc(self):
        a = AdaptiveChunker(threshold=1000)
        assert a.should_inject("hello " * 200)

    def test_not_inject_large_doc(self):
        a = AdaptiveChunker(threshold=1000)
        assert not a.should_inject("hello " * 2000)

    def test_threshold_boundary(self):
        a = AdaptiveChunker(threshold=100)
        assert a.should_inject("hello " * 76)  # 76 words * 1.3 = 98 tokens
        assert not a.should_inject("hello " * 78)  # 78 words * 1.3 = 101 tokens

    def test_disabled(self):
        a = AdaptiveChunker(threshold=1000, enabled=False)
        assert not a.should_inject("hello " * 10)

    def test_no_threshold(self):
        a = AdaptiveChunker()
        assert not a.should_inject("hello world")


class TestAdaptiveChunkerFromConfig:
    """Integration-ish: verify from_config computes threshold correctly."""

    def test_uses_explicit_threshold(self):
        class FakeIngestion:
            adaptive_tiering_enabled = True
            adaptive_tiering_threshold = 5000
            adaptive_tiering_ratio = 0.3

        class FakeLLM:
            context_window_size = 128000

        class FakeConfig:
            ingestion = FakeIngestion()
            llm = FakeLLM()

        a = AdaptiveChunker.from_config(FakeConfig())
        assert a.threshold == 5000
        assert a.should_inject("hello " * 1000)

    def test_uses_ratio_when_no_explicit(self):
        class FakeIngestion:
            adaptive_tiering_enabled = True
            adaptive_tiering_threshold = None
            adaptive_tiering_ratio = 0.5

        class FakeLLM:
            context_window_size = 10000

        class FakeConfig:
            ingestion = FakeIngestion()
            llm = FakeLLM()

        a = AdaptiveChunker.from_config(FakeConfig())
        assert a.threshold == max(1000, int(10000 * 0.5))  # 5000

    def test_min_thousand_floor(self):
        class FakeIngestion:
            adaptive_tiering_enabled = True
            adaptive_tiering_threshold = None
            adaptive_tiering_ratio = 0.01

        class FakeLLM:
            context_window_size = 10000

        class FakeConfig:
            ingestion = FakeIngestion()
            llm = FakeLLM()

        a = AdaptiveChunker.from_config(FakeConfig())
        assert a.threshold == 1000


class TestChunkDataNewFields:
    """Verify new nullable fields on ChunkData (NFR-002)."""

    def test_defaults_are_none(self):
        c = ChunkData(chunk_order=1, text="test")
        assert c.heading_path is None
        assert c.content_type is None
        assert c.adaptive_tier is None

    def test_can_set_fields(self):
        c = ChunkData(
            chunk_order=1,
            text="test",
            heading_path="A > B",
            content_type="text",
            adaptive_tier="full_doc",
        )
        assert c.heading_path == "A > B"
        assert c.content_type == "text"
        assert c.adaptive_tier == "full_doc"
