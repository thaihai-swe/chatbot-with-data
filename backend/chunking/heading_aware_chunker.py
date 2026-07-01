from __future__ import annotations

import re
from chunking.base import BaseChunker, ChunkData


class HeadingAwareChunker(BaseChunker):
    """Chunking strategy that respects heading structure in Markdown/text documents."""

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
        Split text respecting heading boundaries.

        The approach:
        1. Identify heading levels (# ## ### etc for Markdown, or TXT headings)
        2. Group content under each heading, tracking full heading hierarchy
        3. Prepend heading path to every chunk's text
        4. Fall back to fixed-size if no heading structure
        """
        if not text or not text.strip():
            return []

        metadata = metadata or {}

        # Extract sections based on heading structure
        sections = self._extract_sections(text)

        if not sections:
            from chunking.fixed_size_chunker import FixedSizeChunker
            fallback = FixedSizeChunker(
                chunk_size=self.chunk_size,
                overlap=self.overlap
            )
            return fallback.chunk(
                text,
                source_type=source_type,
                title=title,
                page_number=page_number,
                source_url=source_url,
                metadata=metadata
            )

        chunks = []
        chunk_order = 1

        for section in sections:
            section_title = section.get("heading")
            heading_path = section.get("heading_path")
            section_text = section.get("content", "").strip()

            if not section_text:
                continue

            section_chunks = self._chunk_section(
                section_text,
                section_title=section_title,
                heading_path=heading_path,
                chunk_order=chunk_order
            )

            for chunk in section_chunks:
                chunk.title = title
                chunk.page_number = page_number
                chunk.source_url = source_url
                chunk.metadata = {**metadata, **chunk.metadata}
                chunks.append(chunk)
                chunk_order += 1

        return chunks

    def _extract_sections(self, text: str) -> list[dict]:
        """Extract sections based on heading structure with recursive hierarchy."""
        lines = text.split("\n")
        sections = []
        current_section = None
        heading_stack: list[tuple[int, str]] = []  # (level, heading_name)

        for line in lines:
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if heading_match:
                if current_section:
                    sections.append(current_section)

                level = len(heading_match.group(1))
                heading = heading_match.group(2).strip()

                # Pop headings at deeper or equal levels
                while heading_stack and heading_stack[-1][0] >= level:
                    heading_stack.pop()
                heading_stack.append((level, heading))

                heading_path = " > ".join(h[1] for h in heading_stack)

                current_section = {
                    "heading": heading,
                    "level": level,
                    "heading_path": heading_path,
                    "content": ""
                }
            elif current_section is not None:
                current_section["content"] += line + "\n"

        if current_section:
            sections.append(current_section)

        return sections

    def _chunk_section(
        self,
        text: str,
        section_title: str | None = None,
        heading_path: str | None = None,
        chunk_order: int = 1
    ) -> list[ChunkData]:
        """Chunk a single section, prepending heading path to every chunk."""
        chunks = []

        text_tokens = self.estimate_tokens(text)

        if text_tokens <= self.chunk_size:
            chunk_text = text.strip()
            if heading_path:
                chunk_text = f"[{heading_path}] {chunk_text}"
            chunk = ChunkData(
                chunk_order=chunk_order,
                text=chunk_text,
                section_title=section_title,
                heading_path=heading_path,
                metadata={"section_title": section_title} if section_title else {}
            )
            chunks.append(chunk)
        else:
            sentences = text.split(". ")
            current_chunk_tokens = []
            current_token_count = 0

            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                if not sentence.endswith("."):
                    sentence += "."

                sentence_tokens = self.estimate_tokens(sentence)

                if current_token_count + sentence_tokens > self.chunk_size and current_chunk_tokens:
                    chunk_text = " ".join(current_chunk_tokens)
                    if heading_path:
                        chunk_text = f"[{heading_path}] {chunk_text}"
                    chunk = ChunkData(
                        chunk_order=chunk_order,
                        text=chunk_text.strip(),
                        section_title=section_title,
                        heading_path=heading_path,
                        metadata={"section_title": section_title} if section_title else {}
                    )
                    chunks.append(chunk)
                    chunk_order += 1
                    current_chunk_tokens = []
                    current_token_count = 0

                current_chunk_tokens.append(sentence)
                current_token_count += sentence_tokens

            if current_chunk_tokens:
                chunk_text = " ".join(current_chunk_tokens)
                if heading_path:
                    chunk_text = f"[{heading_path}] {chunk_text}"
                chunk = ChunkData(
                    chunk_order=chunk_order,
                    text=chunk_text.strip(),
                    section_title=section_title,
                    heading_path=heading_path,
                    metadata={"section_title": section_title} if section_title else {}
                )
                chunks.append(chunk)

        return chunks
