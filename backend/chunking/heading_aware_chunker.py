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
        2. Group content under each heading
        3. Create chunks that don't cross heading boundaries when possible
        4. Fall back to fixed-size if no heading structure
        """
        if not text or not text.strip():
            return []

        metadata = metadata or {}

        # Extract sections based on heading structure
        sections = self._extract_sections(text)

        if not sections:
            # No heading structure found, fall back to fixed-size
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
            section_text = section.get("content", "").strip()

            if not section_text:
                continue

            # Break section into chunks if it's too large
            section_chunks = self._chunk_section(
                section_text,
                section_title=section_title,
                chunk_order=chunk_order
            )

            for chunk in section_chunks:
                chunk.title = title
                chunk.page_number = page_number
                chunk.source_url = source_url
                # Merge metadata
                chunk.metadata = {**metadata, **chunk.metadata}
                chunks.append(chunk)
                chunk_order += 1

        return chunks

    def _extract_sections(self, text: str) -> list[dict]:
        """Extract sections based on heading structure."""
        lines = text.split("\n")
        sections = []
        current_section = None

        for line in lines:
            # Check for Markdown heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if heading_match:
                # Save previous section if any
                if current_section:
                    sections.append(current_section)

                # Start new section
                level = len(heading_match.group(1))
                heading = heading_match.group(2).strip()
                current_section = {
                    "heading": heading,
                    "level": level,
                    "content": ""
                }
            elif current_section is not None:
                # Add line to current section
                current_section["content"] += line + "\n"

        # Don't forget the last section
        if current_section:
            sections.append(current_section)

        return sections

    def _chunk_section(
        self,
        text: str,
        section_title: str | None = None,
        chunk_order: int = 1
    ) -> list[ChunkData]:
        """Chunk a single section, respecting size limits."""
        chunks = []

        # If section is smaller than chunk_size, keep it whole
        text_tokens = self.estimate_tokens(text)

        if text_tokens <= self.chunk_size:
            chunk = ChunkData(
                chunk_order=chunk_order,
                text=text.strip(),
                section_title=section_title,
                metadata={"section_title": section_title} if section_title else {}
            )
            chunks.append(chunk)
        else:
            # Break section into smaller chunks
            sentences = text.split(". ")
            current_chunk_tokens = []
            current_token_count = 0

            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                # Add period back if not present
                if not sentence.endswith("."):
                    sentence += "."

                sentence_tokens = self.estimate_tokens(sentence)

                if current_token_count + sentence_tokens > self.chunk_size and current_chunk_tokens:
                    # Create chunk
                    chunk_text = " ".join(current_chunk_tokens)
                    chunk = ChunkData(
                        chunk_order=chunk_order,
                        text=chunk_text.strip(),
                        section_title=section_title,
                        metadata={"section_title": section_title} if section_title else {}
                    )
                    chunks.append(chunk)
                    chunk_order += 1
                    current_chunk_tokens = []
                    current_token_count = 0

                current_chunk_tokens.append(sentence)
                current_token_count += sentence_tokens

            # Add final chunk
            if current_chunk_tokens:
                chunk_text = " ".join(current_chunk_tokens)
                chunk = ChunkData(
                    chunk_order=chunk_order,
                    text=chunk_text.strip(),
                    section_title=section_title,
                    metadata={"section_title": section_title} if section_title else {}
                )
                chunks.append(chunk)

        return chunks
