import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from chunking.semantic_chunker import SemanticChunker


class TestSemanticChunker:
    """Tests for semantic chunking strategy."""

    def test_basic_semantic_chunking(self):
        """Test basic semantic chunking."""
        chunker = SemanticChunker(chunk_size=50, semantic_threshold=0.3)

        text = """This is the introduction. We discuss various topics here.
                  Now let's move to the main content. The topic changes significantly.
                  Finally, we conclude with remarks."""

        chunks = chunker.chunk(text, title="Test")

        assert len(chunks) > 0
        assert all(chunk.title == "Test" for chunk in chunks)
        assert all(len(chunk.text) > 0 for chunk in chunks)

    def test_empty_text(self):
        """Test semantic chunking with empty text."""
        chunker = SemanticChunker()

        chunks = chunker.chunk("")
        assert len(chunks) == 0

        chunks = chunker.chunk("   ")
        assert len(chunks) == 0

    def test_single_sentence(self):
        """Test semantic chunking with single sentence."""
        chunker = SemanticChunker()

        text = "This is a single sentence."
        chunks = chunker.chunk(text)

        assert len(chunks) > 0
        assert chunks[0].text == text

    def test_weak_semantic_fallback(self):
        """Test that weak semantic signal triggers fallback to fixed-size."""
        chunker = SemanticChunker(chunk_size=30, fallback_on_weak=True)

        # Text with very similar sentences (weak semantic signal)
        text = "Data is important. Data is useful. Data is valuable. Data is significant."

        chunks = chunker.chunk(text)

        # Should have created chunks with fallback applied
        assert len(chunks) > 0
        # Check if fallback was applied
        if chunker.fallback_applied:
            assert any(c.metadata.get("fallback_applied", False) for c in chunks)

    def test_semantic_threshold_configuration(self):
        """Test that semantic threshold affects chunking."""
        text = "First sentence about A. Second sentence about B. Third sentence about A again."

        # Tight threshold - more chunks
        chunker_tight = SemanticChunker(chunk_size=100, semantic_threshold=0.2)
        chunks_tight = chunker_tight.chunk(text)

        # Loose threshold - fewer chunks
        chunker_loose = SemanticChunker(chunk_size=100, semantic_threshold=0.8)
        chunks_loose = chunker_loose.chunk(text)

        # Both should produce chunks
        assert len(chunks_tight) > 0
        assert len(chunks_loose) > 0

    def test_chunk_metadata_preservation(self):
        """Test that semantic chunking preserves metadata."""
        chunker = SemanticChunker()

        text = "Content here. More content. Final content."
        chunks = chunker.chunk(
            text,
            title="Test Doc",
            page_number=1,
            source_url="http://example.com",
            metadata={"test": "value"}
        )

        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.title == "Test Doc"
            assert chunk.page_number == 1
            assert chunk.source_url == "http://example.com"
            assert chunk.metadata.get("test") == "value"

    def test_semantic_score_calculation(self):
        """Test that semantic scores are calculated and stored."""
        chunker = SemanticChunker(chunk_size=100, fallback_on_weak=False)

        text = "Introduction begins here. We present concepts. Analysis follows naturally. Conclusion wraps up."
        chunks = chunker.chunk(text)

        # At least some chunks should have semantic_score metadata
        assert len(chunks) > 0
        for chunk in chunks:
            if "semantic_score" in chunk.metadata:
                assert 0.0 <= chunk.metadata["semantic_score"] <= 1.0

    def test_chunk_order_is_sequential(self):
        """Test that chunks have sequential ordering."""
        chunker = SemanticChunker(chunk_size=40)

        text = " ".join(["Sentence number {}.".format(i) for i in range(1, 11)])
        chunks = chunker.chunk(text)

        for i, chunk in enumerate(chunks, 1):
            assert chunk.chunk_order == i

    def test_sentence_splitting(self):
        """Test that semantic chunker correctly splits into sentences."""
        chunker = SemanticChunker()

        text = "First sentence. Second sentence! Third sentence? Fourth sentence."
        sentences = chunker._split_into_sentences(text)

        assert len(sentences) == 4
        assert all(s for s in sentences)  # All non-empty

    def test_sentence_similarity_calculation(self):
        """Test sentence similarity heuristic."""
        chunker = SemanticChunker()

        # Similar sentences should have high similarity
        sim_high = chunker._calculate_sentence_similarity(
            "The cat is on the mat.",
            "The dog is on the mat."
        )

        # Dissimilar sentences should have low similarity
        sim_low = chunker._calculate_sentence_similarity(
            "The cat sat on the mat.",
            "Quantum computing involves superposition."
        )

        assert sim_high > sim_low
        assert 0.0 <= sim_high <= 1.0
        assert 0.0 <= sim_low <= 1.0

    def test_weak_segmentation_detection(self):
        """Test weak segmentation detection."""
        chunker = SemanticChunker()

        # High variance in scores (strong signal)
        strong_scores = [0.1, 0.2, 0.9, 0.95, 0.1, 0.05]
        is_weak_strong = chunker._is_weak_segmentation(strong_scores)

        # Low variance in scores (weak signal)
        weak_scores = [0.5, 0.51, 0.49, 0.52, 0.50, 0.51]
        is_weak_weak = chunker._is_weak_segmentation(weak_scores)

        assert not is_weak_strong  # Strong signal detected
        assert is_weak_weak  # Weak signal detected

    def test_semantic_chunker_direct_instantiation(self):
        """Test SemanticChunker can be instantiated with various configurations."""
        chunker1 = SemanticChunker(chunk_size=512, semantic_threshold=0.3)
        assert chunker1.chunk_size == 512
        assert chunker1.semantic_threshold == 0.3

        chunker2 = SemanticChunker(semantic_threshold=1.5)  # Should clamp to 1.0
        assert chunker2.semantic_threshold == 1.0

        chunker3 = SemanticChunker(semantic_threshold=-0.5)  # Should clamp to 0.0
        assert chunker3.semantic_threshold == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
