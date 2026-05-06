from __future__ import annotations

from chunking.base import BaseChunker, ChunkData
from chunking.fixed_size_chunker import FixedSizeChunker


class PageAwareChunker(BaseChunker):
    """Chunking strategy that respects page boundaries in PDF documents."""

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
        Split text while respecting page boundaries.

        Expects text to be pre-formatted with page markers (###PAGE_BREAK### or similar).
        If no page markers found, falls back to fixed-size chunking.
        """
        if not text or not text.strip():
            return []

        metadata = metadata or {}

        # Split on page breaks
        page_marker = "###PAGE_BREAK###"
        pages = text.split(page_marker)

        chunks = []
        chunk_order = 1

        for page_idx, page_text in enumerate(pages):
            page_text = page_text.strip()

            if not page_text:
                continue

            current_page_number = page_number if page_number is not None else (page_idx + 1)

            # Chunk this page
            page_chunks = self._chunk_page(
                page_text,
                page_number=current_page_number,
                chunk_order=chunk_order,
                title=title,
                source_url=source_url,
                metadata=metadata
            )

            chunks.extend(page_chunks)
            chunk_order += len(page_chunks)

        # If no page breaks found, fall back to fixed-size
        if len(pages) == 1 and len(chunks) == 0:
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

        return chunks

    def _chunk_page(
        self,
        page_text: str,
        page_number: int,
        chunk_order: int,
        title: str | None = None,
        source_url: str | None = None,
        metadata: dict | None = None
    ) -> list[ChunkData]:
        """Chunk a single page of text."""
        chunks = []
        metadata = metadata or {}

        page_metadata = {**metadata, "page_number": page_number}

        # If page is smaller than chunk size, keep it as one chunk
        page_tokens = self.estimate_tokens(page_text)

        if page_tokens <= self.chunk_size:
            chunk = ChunkData(
                chunk_order=chunk_order,
                text=page_text,
                title=title,
                page_number=page_number,
                source_url=source_url,
                metadata=page_metadata
            )
            chunks.append(chunk)
        else:
            # Split page into smaller chunks
            # Use fixed-size chunking within the page
            sentences = page_text.split(".")
            current_chunk_tokens = []
            current_token_count = 0

            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                # Add period back
                sentence_text = sentence + "." if not sentence.endswith(".") else sentence
                sentence_tokens = self.estimate_tokens(sentence_text)

                if current_token_count + sentence_tokens > self.chunk_size and current_chunk_tokens:
                    # Create chunk
                    chunk_text = " ".join(current_chunk_tokens)
                    chunk = ChunkData(
                        chunk_order=chunk_order,
                        text=chunk_text.strip(),
                        title=title,
                        page_number=page_number,
                        source_url=source_url,
                        metadata=page_metadata
                    )
                    chunks.append(chunk)
                    chunk_order += 1
                    current_chunk_tokens = []
                    current_token_count = 0

                current_chunk_tokens.append(sentence_text)
                current_token_count += sentence_tokens

            # Add final chunk
            if current_chunk_tokens:
                chunk_text = " ".join(current_chunk_tokens)
                chunk = ChunkData(
                    chunk_order=chunk_order,
                    text=chunk_text.strip(),
                    title=title,
                    page_number=page_number,
                    source_url=source_url,
                    metadata=page_metadata
                )
                chunks.append(chunk)

        return chunks
