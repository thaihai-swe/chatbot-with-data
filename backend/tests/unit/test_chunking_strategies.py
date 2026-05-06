import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from chunking.fixed_size_chunker import FixedSizeChunker
from chunking.heading_aware_chunker import HeadingAwareChunker
from chunking.page_aware_chunker import PageAwareChunker
from chunking.dispatcher import ChunkingDispatcher


class TestFixedSizeChunker:
    """Tests for fixed-size chunking strategy."""

    def test_basic_chunking(self):
        chunker = FixedSizeChunker(chunk_size=50, overlap=0)
        text = "This is sentence one. This is sentence two. This is sentence three."
        chunks = chunker.chunk(text, title="Test")

        assert len(chunks) > 0
        assert all(chunk.title == "Test" for chunk in chunks)
        assert chunks[0].chunk_order == 1

    def test_empty_text(self):
        chunker = FixedSizeChunker()
        chunks = chunker.chunk("")
        assert len(chunks) == 0

    def test_small_text(self):
        chunker = FixedSizeChunker(chunk_size=100)
        text = "Short text."
        chunks = chunker.chunk(text)
        assert len(chunks) == 1
        assert chunks[0].text == "Short text."

    def test_chunk_order(self):
        chunker = FixedSizeChunker(chunk_size=30)
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        chunks = chunker.chunk(text)

        for i, chunk in enumerate(chunks, 1):
            assert chunk.chunk_order == i


class TestHeadingAwareChunker:
    """Tests for heading-aware chunking strategy."""

    def test_markdown_sections(self):
        chunker = HeadingAwareChunker(chunk_size=100)
        text = """
# Chapter 1
This is intro content under chapter 1.

## Section 1.1
More content here for section 1.1.

# Chapter 2
Content under chapter 2.
"""
        chunks = chunker.chunk(text)

        assert len(chunks) > 0
        # Find chunks with section titles
        section_chunks = [c for c in chunks if c.section_title]
        assert len(section_chunks) > 0

    def test_no_heading_fallback(self):
        chunker = HeadingAwareChunker(chunk_size=50)
        text = "This is plain text without any headings. Just sentences separated by periods."
        chunks = chunker.chunk(text)

        # Should fall back to fixed-size and produce chunks
        assert len(chunks) > 0


class TestPageAwareChunker:
    """Tests for page-aware chunking strategy."""

    def test_page_boundaries(self):
        chunker = PageAwareChunker(chunk_size=100)
        text = "Page 1 content here.###PAGE_BREAK###Page 2 content here.###PAGE_BREAK###Page 3 content here."
        chunks = chunker.chunk(text)

        assert len(chunks) > 0
        # Check page numbers
        page_numbers = [c.page_number for c in chunks]
        assert 1 in page_numbers
        assert 2 in page_numbers
        assert 3 in page_numbers

    def test_no_page_break_fallback(self):
        chunker = PageAwareChunker(chunk_size=50)
        text = "This is a single page without page breaks."
        chunks = chunker.chunk(text)

        # Should fall back to fixed-size
        assert len(chunks) > 0


class TestChunkingDispatcher:
    """Tests for chunking dispatcher."""

    def test_get_strategies(self):
        strategies = ChunkingDispatcher.get_available_strategies()
        assert "fixed_size" in strategies
        assert "heading_aware" in strategies
        assert "page_aware" in strategies

    def test_default_strategy_by_source(self):
        assert ChunkingDispatcher.get_default_strategy("pdf") == "page_aware"
        assert ChunkingDispatcher.get_default_strategy("md") == "heading_aware"
        assert ChunkingDispatcher.get_default_strategy("txt") == "fixed_size"

    def test_dispatcher_chunk(self):
        text = "This is a test. It has multiple sentences. Each one is separate."
        chunks = ChunkingDispatcher.chunk(text, strategy="fixed_size", chunk_size=50)

        assert len(chunks) > 0
        assert all(hasattr(c, 'text') for c in chunks)

    def test_invalid_strategy(self):
        with pytest.raises(ValueError):
            ChunkingDispatcher.chunk("text", strategy="invalid_strategy")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
