from __future__ import annotations

import pytest

from chunking.parent_child_chunker import ParentChildChunker


class TestParentChildChunker:
    """Unit tests for ParentChildChunker boundary-aware grouping (AC-009 / REQ-006)."""

    def test_multi_section_with_headings(self):
        p = ParentChildChunker(512)
        chunks = p.chunk("# Introduction\nIntro content here.\n## Background\nBackground details.\n# Conclusion\nFinal thoughts.")
        parents = [c for c in chunks if c.metadata.get("parent_chunk")]
        children = [c for c in chunks if not c.metadata.get("parent_chunk")]
        assert len(parents) >= 1
        assert len(children) >= 1

    def test_no_headings_fallback_to_fixed_count(self):
        p = ParentChildChunker(100, children_per_parent=3)
        chunks = p.chunk("This is sentence one. " * 20 + "That is sentence two. " * 20)
        parents = [c for c in chunks if c.metadata.get("parent_chunk")]
        assert len(parents) >= 1
        for parent in parents:
            assert parent.metadata["children_count"] >= 1

    def test_parent_metadata(self):
        p = ParentChildChunker(100)
        chunks = p.chunk("Word sentence one. " * 15 + "Another sentence. " * 15)
        parents = [c for c in chunks if c.metadata.get("parent_chunk")]
        for parent in parents:
            assert parent.section_title == "Expanded Context"
            assert parent.metadata["parent_chunk"] is True
            assert parent.metadata["children_count"] >= 1

    def test_empty_text(self):
        p = ParentChildChunker(512)
        assert p.chunk("") == []

    def test_parents_ordered_after_children(self):
        p = ParentChildChunker(100)
        chunks = p.chunk("Sentence. " * 30)
        children = [c for c in chunks if not c.metadata.get("parent_chunk")]
        parents = [c for c in chunks if c.metadata.get("parent_chunk")]
        if children and parents:
            assert children[-1].chunk_order < parents[0].chunk_order

    def test_detect_section_boundaries(self):
        p = ParentChildChunker(512)
        boundaries = p._detect_section_boundaries("# A\n# B\n## C\nD\n# E")
        assert len(boundaries) == 4
        text_positions = [p._detect_section_boundaries("# A\n# B\n## C\nD\n# E")]
        assert len(text_positions[0]) == 4

    def test_group_fixed_count_children(self):
        p = ParentChildChunker(100)
        chunks = p.chunk("Word. " * 50)
        children = [c for c in chunks if not c.metadata.get("parent_chunk")]
        groups = p._group_fixed_count(children)
        assert len(groups) >= 1
