import re

from backend.utils import generate_id, json_dumps, sha256_text, utcnow_iso


class ChunkingService:
    def __init__(self, chunk_size=512, chunk_overlap=64):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def create_chunks(self, document):
        raw_text = document.get("raw_text") or ""
        source_type = document["source_type"]
        metadata = {
            "document_id": document["document_id"],
            "collection_id": document.get("collection_id"),
            "source_type": source_type,
            "title": document.get("title"),
            "source_url": document.get("source_url"),
        }

        if source_type == "markdown":
            return self._chunk_markdown(raw_text, metadata)
        if source_type == "pdf":
            freshness = document.get("freshness_metadata") or "{}"
            return self._chunk_pdf(raw_text, metadata, freshness)
        return self._chunk_fixed(raw_text, metadata)

    def _base_chunk(self, metadata, chunk_text, chunk_order, section_name=None, page_number=None):
        return {
            "chunk_id": generate_id("chunk"),
            "document_id": metadata["document_id"],
            "collection_id": metadata.get("collection_id"),
            "source_type": metadata["source_type"],
            "title": metadata.get("title"),
            "source_url": metadata.get("source_url"),
            "section_name": section_name,
            "page_number": page_number,
            "chunk_order": chunk_order,
            "chunk_text": chunk_text,
            "content_hash": sha256_text(chunk_text),
            "parent_chunk_id": None,
            "child_chunk_ids_json": None,
            "semantic_metadata_json": json_dumps({}),
            "created_at": utcnow_iso(),
        }

    def _slice_text(self, text):
        text = text.strip()
        if not text:
            return []
        chunks = []
        step = max(1, self.chunk_size - self.chunk_overlap)
        for start in range(0, len(text), step):
            end = start + self.chunk_size
            segment = text[start:end].strip()
            if segment:
                chunks.append(segment)
            if end >= len(text):
                break
        return chunks

    def _chunk_fixed(self, text, metadata):
        return [
            self._base_chunk(metadata, chunk_text, index)
            for index, chunk_text in enumerate(self._slice_text(text), start=1)
        ]

    def _chunk_markdown(self, text, metadata):
        parts = re.split(r"(?m)^(#{1,6}\s+.+)$", text)
        chunks = []
        current_heading = None
        buffer = ""
        order = 1

        for part in parts:
            stripped = part.strip()
            if not stripped:
                continue
            if re.match(r"^#{1,6}\s+", stripped):
                if buffer.strip():
                    for segment in self._slice_text(buffer):
                        chunks.append(
                            self._base_chunk(
                                metadata,
                                segment,
                                order,
                                section_name=current_heading,
                            )
                        )
                        order += 1
                    buffer = ""
                current_heading = stripped.lstrip("#").strip()
            else:
                buffer = f"{buffer}\n{stripped}".strip()

        if buffer.strip():
            for segment in self._slice_text(buffer):
                chunks.append(
                    self._base_chunk(metadata, segment, order, section_name=current_heading)
                )
                order += 1

        return chunks or self._chunk_fixed(text, metadata)

    def _chunk_pdf(self, text, metadata, freshness_metadata):
        chunks = []
        order = 1
        page_texts = []
        try:
            import json

            page_texts = json.loads(freshness_metadata).get("page_texts", [])
        except Exception:
            page_texts = []

        if not page_texts:
            return self._chunk_fixed(text, metadata)

        for page_number, page_text in enumerate(page_texts, start=1):
            for segment in self._slice_text(page_text):
                chunks.append(
                    self._base_chunk(
                        metadata,
                        segment,
                        order,
                        page_number=page_number,
                    )
                )
                order += 1
        return chunks
