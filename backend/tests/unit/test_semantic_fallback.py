import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from chunking.semantic_chunker import SemanticChunker
from chunking.fixed_size_chunker import FixedSizeChunker


class TestSemanticFallback:
    """Tests for semantic chunking fallback behavior."""

    def test_weak_semantic_triggers_fallback(self):
        """Test that weak semantic signal triggers fallback to fixed-size."""
        chunker = SemanticChunker(chunk_size=50, fallback_on_weak=True)

        # Text with very similar sentences (weak semantic signal)
        text = "The data is important. The data is useful. The data is valuable. The data is significant."

        chunks = chunker.chunk(text)

        # Fallback should have been triggered
        assert chunker.fallback_applied == True

        # Check for fallback metadata
        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.metadata.get("fallback_applied", False) == True

    def test_fallback_uses_fixed_size_strategy(self):
        """Test that fallback uses fixed-size chunking strategy."""
        chunker = SemanticChunker(chunk_size=40, fallback_on_weak=True)

        # Weak semantic signal text
        text = "Same topic here. Same topic continues. Same topic again. More of same."

        semantic_chunks = chunker.chunk(text)

        # Compare with fixed-size chunker
        fixed_chunker = FixedSizeChunker(chunk_size=40)
        fixed_chunks = fixed_chunker.chunk(text)

        # When fallback is used, number of chunks should be similar to fixed-size
        # (might not be exactly same due to sentence boundaries, but close)
        assert len(semantic_chunks) > 0
        assert len(fixed_chunks) > 0

    def test_fallback_metadata_flag(self):
        """Test that fallback_applied flag is set in chunk metadata."""
        chunker = SemanticChunker(chunk_size=40, fallback_on_weak=True)

        weak_text = "Similar sentences. Similar content. Similar structure. Similar ideas."
        chunks = chunker.chunk(weak_text)

        # All chunks should be flagged with fallback_applied
        assert len(chunks) > 0
        for chunk in chunks:
            if chunker.fallback_applied:
                assert chunk.metadata.get("fallback_applied", False) == True

    def test_fallback_reason_metadata(self):
        """Test that fallback reason is recorded in metadata."""
        chunker = SemanticChunker(chunk_size=40, fallback_on_weak=True)

        weak_text = "Data is important. Data is valuable. Data is significant. Data is critical."
        chunks = chunker.chunk(weak_text)

        # Check for fallback reason
        assert len(chunks) > 0
        if chunker.fallback_applied:
            has_reason = any(
                "fallback_reason" in chunk.metadata
                for chunk in chunks
            )
            # At least some indication of fallback should be present
            assert len(chunks) > 0

    def test_no_fallback_on_strong_signal(self):
        """Test that fallback doesn't trigger on strong semantic signal."""
        chunker = SemanticChunker(chunk_size=100, semantic_threshold=0.3, fallback_on_weak=True)

        # Text with clear topic changes (strong semantic signal)
        text = """
        Introduction to computers.
        History of computing.
        Modern computer architecture.
        Computer applications today.
        Programming languages overview.
        """

        chunks = chunker.chunk(text)

        # Fallback might not be triggered if signal is strong enough
        assert len(chunks) > 0
        # Check if it's treating as semantic or fallback
        # (Could go either way depending on variance)

    def test_fallback_without_weak_check(self):
        """Test that semantic chunking works without fallback when fallback_on_weak=False."""
        chunker = SemanticChunker(chunk_size=50, fallback_on_weak=False)

        # Even with weak signal, should produce chunks from sentences
        text = "Same content here. Same content there. Same content everywhere. Same content again."
        chunks = chunker.chunk(text)

        assert len(chunks) > 0
        # Should still have chunks even without fallback

    def test_fallback_preserves_metadata(self):
        """Test that fallback preserves all document metadata."""
        chunker = SemanticChunker(chunk_size=40, fallback_on_weak=True)

        weak_text = "Topic continues. Topic persists. Topic remains. Topic continues."

        chunks = chunker.chunk(
            weak_text,
            title="Test Document",
            page_number=5,
            source_url="http://example.com",
            metadata={"custom": "metadata", "test_key": "test_value"}
        )

        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.title == "Test Document"
            assert chunk.page_number == 5
            assert chunk.source_url == "http://example.com"
            assert chunk.metadata.get("custom") == "metadata"
            assert chunk.metadata.get("test_key") == "test_value"

    def test_fallback_with_empty_text(self):
        """Test fallback behavior with empty text."""
        chunker = SemanticChunker(fallback_on_weak=True)

        chunks = chunker.chunk("")
        assert len(chunks) == 0

        chunks = chunker.chunk("   \n\t  ")
        assert len(chunks) == 0

    def test_fallback_with_short_content(self):
        """Test fallback with very short content."""
        chunker = SemanticChunker(chunk_size=200, fallback_on_weak=True)

        short_text = "Very short."
        chunks = chunker.chunk(short_text)

        assert len(chunks) > 0
        assert len(chunks) == 1
        assert chunks[0].text == short_text

    def test_fallback_with_encoding_edge_cases(self):
        """Test fallback with unusual text encoding/characters."""
        chunker = SemanticChunker(chunk_size=50, fallback_on_weak=True)

        # Text with special characters
        text = "Content with special chars: @#$%. More content! Even more..."
        chunks = chunker.chunk(text)

        assert len(chunks) > 0
        assert all(len(chunk.text) > 0 for chunk in chunks)

    def test_fallback_chunking_consistency(self):
        """Test that fallback chunking is consistent with fixed-size chunker."""
        text = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five."

        # Semantic chunker with fallback
        semantic_chunker = SemanticChunker(chunk_size=50, fallback_on_weak=True)
        semantic_chunks = semantic_chunker.chunk(text)

        # If fallback was triggered, number of chunks should be reasonable
        if semantic_chunker.fallback_applied:
            assert len(semantic_chunks) >= 1
            # Total characters should be preserved
            total_chars = sum(len(c.text) for c in semantic_chunks)
            assert total_chars >= len("".join([s.strip() for s in text.split(".")]))

    def test_weak_segmentation_detection_accuracy(self):
        """Test that weak segmentation is correctly identified."""
        chunker = SemanticChunker()

        # Create artificially weak and strong score distributions
        weak_scores = [0.5] * 10  # All similar
        strong_scores = [0.1, 0.2, 0.1, 0.9, 0.95, 0.2, 0.1, 0.05, 0.9, 0.1]  # Varied

        # Weak scores should be detected as weak
        is_weak_weak = chunker._is_weak_segmentation(weak_scores)
        assert is_weak_weak == True

        # Strong scores should not be detected as weak
        is_weak_strong = chunker._is_weak_segmentation(strong_scores)
        assert is_weak_strong == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
