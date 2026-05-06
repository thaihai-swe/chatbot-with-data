from __future__ import annotations

from chunking.base import BaseChunker, ChunkData


class FixedSizeChunker(BaseChunker):
    """Chunking strategy that splits text into fixed-size chunks with overlap."""

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
        Split text into fixed-size chunks.

        The approach:
        1. Split text into paragraphs/sentences
        2. Group into chunks not exceeding chunk_size
        3. Apply overlap between consecutive chunks
        """
        if not text or not text.strip():
            return []

        metadata = metadata or {}
        chunks = []

        # Split into sentences for better boundaries
        sentences = self._split_into_sentences(text)

        if not sentences:
            # Fall back to word splitting if no sentence boundaries
            sentences = text.split()

        current_chunk_tokens = []
        current_token_count = 0
        chunk_order = 1
        overlap_tokens = []

        for sentence in sentences:
            # Estimate token count for this sentence
            sentence_tokens = int(self.estimate_tokens(sentence))

            # Check if adding this sentence would exceed chunk size
            if current_token_count + sentence_tokens > self.chunk_size and current_chunk_tokens:
                # Create chunk from accumulated tokens
                chunk_text = " ".join(current_chunk_tokens).strip()

                if chunk_text:
                    chunk = ChunkData(
                        chunk_order=chunk_order,
                        text=chunk_text,
                        title=title,
                        section_title=None,
                        page_number=page_number,
                        source_url=source_url,
                        metadata=metadata
                    )
                    chunks.append(chunk)
                    chunk_order += 1

                    # Preserve overlap for next chunk
                    if self.overlap > 0:
                        overlap_tokens = current_chunk_tokens[-(self.overlap // 10):]
                    else:
                        overlap_tokens = []

                # Start new chunk with overlap
                current_chunk_tokens = overlap_tokens + [sentence]
                current_token_count = len(overlap_tokens) + sentence_tokens
            else:
                # Add sentence to current chunk
                current_chunk_tokens.append(sentence)
                current_token_count += sentence_tokens

        # Add final chunk
        if current_chunk_tokens:
            chunk_text = " ".join(current_chunk_tokens).strip()
            if chunk_text:
                chunk = ChunkData(
                    chunk_order=chunk_order,
                    text=chunk_text,
                    title=title,
                    section_title=None,
                    page_number=page_number,
                    source_url=source_url,
                    metadata=metadata
                )
                chunks.append(chunk)

        return chunks

    @staticmethod
    def _split_into_sentences(text: str) -> list[str]:
        """Split text into sentences on common delimiters."""
        import re

        # Replace multiple spaces/newlines with single space
        text = re.sub(r'\s+', ' ', text)

        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)

        return [s.strip() for s in sentences if s.strip()]
