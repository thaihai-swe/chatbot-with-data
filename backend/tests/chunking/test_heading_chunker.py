from __future__ import annotations

import pytest

from chunking.heading_aware_chunker import HeadingAwareChunker


class TestHeadingAwareChunker:
    """Tests for heading context preservation (AC-004)."""

    def test_heading_path_prepended_to_all_chunks(self):
        h = HeadingAwareChunker(50)
        chunks = h.chunk('# A\n## B\n### C\n' + 'word ' * 500)
        assert len(chunks) >= 1
        assert all('[A > B > C]' in c.text for c in chunks)

    def test_single_level_heading(self):
        h = HeadingAwareChunker(100)
        chunks = h.chunk('# Title\nSome content here. ' * 10)
        assert all('[Title]' in c.text for c in chunks)

    def test_flat_headings_separate(self):
        h = HeadingAwareChunker(200)
        chunks = h.chunk('# A\nContent A.\n' * 5 + '# B\nContent B.\n' * 5)
        a_chunks = [c for c in chunks if c.heading_path == 'A']
        b_chunks = [c for c in chunks if c.heading_path == 'B']
        assert len(a_chunks) >= 1
        assert len(b_chunks) >= 1

    def test_no_headings_falls_back(self):
        h = HeadingAwareChunker(100)
        chunks = h.chunk("Some plain text. " * 50)
        assert len(chunks) >= 1

    def test_empty_text(self):
        h = HeadingAwareChunker(100)
        assert h.chunk("") == []
        assert h.chunk("   ") == []
