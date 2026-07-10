"""Service for assembling context from retrieval results and chat history."""
from __future__ import annotations

import json
import logging
from typing import List, Dict, Any, Optional

from database import get_connection
from models.chat import ChatTurn
from config import get_settings, get_config
from repositories.chunk_repository import ChunkRepository
from repositories.document_repository import DocumentRepository

logger = logging.getLogger(__name__)

def load_chunk_notes(chunk_ids: List[str]) -> Dict[str, str]:
    """Query chunk_notes for the given chunk IDs.
    
    Returns a dict mapping chunk_id -> note_text.
    """
    if not chunk_ids:
        return {}
    placeholders = ",".join("?" for _ in chunk_ids)
    query = f"SELECT chunk_id, note_text FROM chunk_notes WHERE chunk_id IN ({placeholders})"
    with get_connection() as connection:
        rows = connection.execute(query, chunk_ids).fetchall()
    return {row["chunk_id"]: row["note_text"] for row in rows}


from chat.prompts import get_grounded_system_prompt, CONFLICT_INSTRUCTION, UNCERTAINTY_INSTRUCTION

class ContextService:
    """Service for building LLM prompt context."""

    def __init__(self, max_history_turns: int = 10):
        """
        Initialize the context service.

        Args:
            max_history_turns: Maximum number of previous turns to include in context
        """
        self.max_history_turns = max_history_turns

    def assemble_context(
        self,
        query_text: str,
        retrieved_chunks: List[Dict[str, Any]],
        chat_history: List[ChatTurn],
        collection_ids: Optional[List[str]] = None,
        annotations: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Assemble the full context for an LLM prompt.

        Args:
            query_text: The current user query
            retrieved_chunks: List of retrieved chunk metadata
            chat_history: List of previous turns in the session
            collection_ids: Optional list of collection IDs for document enrichment
            annotations: Optional dict mapping chunk_id -> note_text to inject into <source> tags

        Returns:
            Dict containing system prompt, user prompt, and metadata
        """
        # 1. Build enriched blocks from document understanding data
        summaries_block = ""
        citation_map_block = ""
        if collection_ids and retrieved_chunks:
            summaries_block, citation_map_block = self._build_enriched_blocks(retrieved_chunks)

        # 2. Format retrieved chunks into a context string
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            source_label = f"Source {i+1}"
            source_id = chunk.get('chunk_id', 'unknown')
            title = chunk.get('title', 'Unknown')
            page = chunk.get('page_number', 'N/A')
            section = chunk.get('section_title') or chunk.get('metadata', {}).get('section_path', '')

            chunk_text = chunk.get("text")
            if not chunk_text and chunk.get("chunk_id"):
                try:
                    repo = ChunkRepository()
                    record = repo.get_chunk(chunk["chunk_id"])
                    chunk_text = record.get("text") if record else ""
                except Exception:
                    chunk_text = ""

            block_lines = []
            block_lines.append(f"[Source {source_id}]")
            block_lines.append(f"Title: {title}")
            block_lines.append(f"Page: {page}")
            if section:
                block_lines.append(f"Section: {section}")
            if annotations and source_id in annotations:
                block_lines.append(f"Note: {annotations[source_id]}")
            block_lines.append(f"Content: {chunk_text}")
            
            part = "\n".join(block_lines)
            context_parts.append(part)

        context_string = "\n\n".join(context_parts)

        # 3. Combine enriched blocks with context string
        full_context = ""
        if summaries_block:
            full_context += summaries_block + "\n\n"
        if citation_map_block:
            full_context += citation_map_block + "\n\n"
        full_context += context_string

        # 4. Format chat history
        recent_history = chat_history[-self.max_history_turns:] if chat_history else []

        formatted_history = []
        for turn in recent_history:
            formatted_history.append({"role": "user", "content": turn.query_text})
            if turn.answer_text:
                formatted_history.append({"role": "assistant", "content": turn.answer_text})

        # 5. Determine conflict instruction (only when multiple documents)
        unique_doc_ids = set()
        for chunk in retrieved_chunks:
            doc_id = chunk.get("document_id")
            if doc_id:
                unique_doc_ids.add(doc_id)
        has_conflict = len(unique_doc_ids) > 1
        conflict_instruction_str = CONFLICT_INSTRUCTION + "\n" if has_conflict else ""
        uncertainty_instruction_str = UNCERTAINTY_INSTRUCTION + "\n"

        # 6. Assemble the final context package
        system_prompt = get_grounded_system_prompt(
            full_context,
            conflict_instruction=conflict_instruction_str,
            uncertainty_instruction=uncertainty_instruction_str,
        )

        return {
            "system_prompt": system_prompt,
            "context_string": full_context,
            "history": formatted_history,
            "current_query": query_text,
            "metadata": {
                "num_chunks": len(retrieved_chunks),
                "num_history_turns": len(recent_history),
            }
        }

    def _build_enriched_blocks(
        self, retrieved_chunks: List[Dict[str, Any]]
    ) -> tuple[str, str]:
        """Build optional <document-summaries> and <citation-map> blocks."""
        doc_ids = set()
        for chunk in retrieved_chunks:
            doc_id = chunk.get("document_id")
            if doc_id:
                doc_ids.add(doc_id)

        if not doc_ids:
            return "", ""

        doc_repo = DocumentRepository()
        docs = doc_repo.get_document_batch(list(doc_ids))
        if not docs:
            return "", ""

        summaries_parts = []
        citation_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            doc_id = chunk.get("document_id")
            source_label = f"Source {i+1}"
            doc = docs.get(doc_id) if doc_id else None

            if doc:
                meta = doc.get("metadata", {}) or {}
                understanding = meta.get("doc_understanding") if isinstance(meta, dict) else None

                if understanding and understanding.get("summary"):
                    title = doc.get("title", "Unknown")
                    summaries_parts.append(
                        f'<document id="{doc_id}" title="{title}">\n'
                        f"Summary: {understanding['summary']}\n"
                        f"Topics: {', '.join(understanding.get('topics', []))}\n"
                        f"</document>"
                    )

                section = (
                    chunk.get("section_title")
                    or chunk.get("metadata", {}).get("section_path", "")
                    or "N/A"
                )
                title = (doc.get("title") or chunk.get("title") or "Unknown")
                citation_parts.append(
                    f'[{source_label}] → "{title}", Section "{section}"'
                )

        summaries_block = ""
        if summaries_parts:
            summaries_block = "<document-summaries>\n" + "\n\n".join(summaries_parts) + "\n</document-summaries>"

        citation_map_block = ""
        if citation_parts:
            citation_map_block = "<citation-map>\n" + "\n".join(citation_parts) + "\n</citation-map>"

        return summaries_block, citation_map_block


def get_context_service() -> ContextService:
    """Factory function for ContextService."""
    config = get_config()
    return ContextService(max_history_turns=config.llm.chat_history_limit)
