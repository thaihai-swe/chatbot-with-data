"""Service for assembling context from retrieval results and chat history."""
from __future__ import annotations

import logging
from typing import List, Dict, Any

from models.chat import ChatTurn
from config import get_settings
from repositories.chunk_repository import ChunkRepository

logger = logging.getLogger(__name__)


from chat.prompts import get_grounded_system_prompt

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
    ) -> Dict[str, Any]:
        """
        Assemble the full context for an LLM prompt.

        Args:
            query_text: The current user query
            retrieved_chunks: List of retrieved chunk metadata
            chat_history: List of previous turns in the session

        Returns:
            Dict containing system prompt, user prompt, and metadata
        """
        # 1. Format retrieved chunks into a context string
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            # Include source info for grounding
            source_label = f"Source {i+1}"
            source_id = chunk.get('chunk_id', 'unknown')
            title = chunk.get('title', 'Unknown')
            page = chunk.get('page_number', 'N/A')

            # Ensure we have the chunk text; retrieval may only return metadata
            chunk_text = chunk.get("text")
            if not chunk_text and chunk.get("chunk_id"):
                # Try to load from DB as a fallback
                try:
                    repo = ChunkRepository()
                    record = repo.get_chunk(chunk["chunk_id"])
                    chunk_text = record.get("text") if record else ""
                except Exception:
                    chunk_text = ""

            part = f'<source label="{source_label}" id="{source_id}" title="{title}" page="{page}">\n{chunk_text}\n</source>'
            context_parts.append(part)

        context_string = "\n\n".join(context_parts)

        # 2. Format chat history
        # Only take the last N turns
        recent_history = chat_history[-self.max_history_turns:] if chat_history else []

        formatted_history = []
        for turn in recent_history:
            formatted_history.append({"role": "user", "content": turn.query_text})
            if turn.answer_text:
                formatted_history.append({"role": "assistant", "content": turn.answer_text})

        # 3. Assemble the final context package
        system_prompt = get_grounded_system_prompt(context_string)

        return {
            "system_prompt": system_prompt,
            "context_string": context_string,
            "history": formatted_history,
            "current_query": query_text,
            "metadata": {
                "num_chunks": len(retrieved_chunks),
                "num_history_turns": len(recent_history),
            }
        }


def get_context_service() -> ContextService:
    """Factory function for ContextService."""
    settings = get_settings()
    return ContextService(max_history_turns=settings.max_history_turns)
