from __future__ import annotations

import json
import logging
from typing import List, Dict, Any

from providers.base import BaseLLMProvider
from database import get_connection
from repositories.collection_repository import CollectionRepository
from chat.prompts import (
    STUDY_GUIDE_PROMPT,
    BRIEFING_DOC_PROMPT,
    FAQ_PROMPT,
    TIMELINE_PROMPT,
    GLOSSARY_PROMPT,
    FLASHCARDS_PROMPT
)
from chat.utils import parse_json_from_llm

logger = logging.getLogger(__name__)

class KnowledgeProductService:
    def __init__(self, llm_provider: BaseLLMProvider, collection_repository: CollectionRepository = None):
        self.llm_provider = llm_provider
        self.collection_repository = collection_repository or CollectionRepository()

    def _get_document_summary(self, doc: dict[str, Any]) -> str:
        """Extract pre-computed summary or generate on-the-fly summary of first 3 chunks."""
        metadata = doc.get("metadata", {})
        doc_understanding = metadata.get("doc_understanding")
        
        if doc_understanding and isinstance(doc_understanding, dict):
            summary = doc_understanding.get("summary", "")
            topics = doc_understanding.get("topics", [])
            return f"Document: {doc.get('title')}\nSummary: {summary}\nTopics: {', '.join(topics)}\n"
        
        doc_id = doc.get("id")
        title = doc.get("title", "Untitled")
        logger.info(f"Generating fallback summary for document {doc_id} ('{title}').")
        
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT text FROM chunks WHERE document_id = ? ORDER BY chunk_order ASC LIMIT 3",
                (doc_id,)
            ).fetchall()
        
        chunk_texts = [row[0] for row in rows]
        if not chunk_texts:
            extracted_text = doc.get("extracted_text", "")
            if extracted_text:
                chunk_texts = [extracted_text[:1500]]
            else:
                return f"Document: {title}\nNo content available.\n"
        
        context = "\n\n".join(chunk_texts)
        prompt = f"Please generate a 2-3 sentence summary of the following document content.\n\nDocument Title: {title}\n\nContent:\n{context}\n\nSummary:"
        try:
            summary = self.llm_provider.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            ).strip()
            return f"Document: {title}\nSummary: {summary}\n"
        except Exception as e:
            logger.error(f"Failed to generate fallback summary for {doc_id}: {e}")
            return f"Document: {title}\nSummary: Summary generation failed.\n"

    def _assemble_collection_context(self, collection_id: str) -> str:
        """Retrieve all collection documents and construct a joint summary context."""
        docs = self.collection_repository.get_collection_members(collection_id)
        if not docs:
            raise ValueError(f"Collection {collection_id} has no documents.")
            
        summaries = []
        for doc in docs:
            summaries.append(self._get_document_summary(doc))
            
        return "\n---\n".join(summaries)

    def generate_study_guide(self, collection_id: str) -> str:
        context_text = self._assemble_collection_context(collection_id)
        prompt = STUDY_GUIDE_PROMPT.format(context_text=context_text)
        return self.llm_provider.generate_completion([{"role": "user", "content": prompt}])

    def generate_briefing_doc(self, collection_id: str) -> str:
        context_text = self._assemble_collection_context(collection_id)
        prompt = BRIEFING_DOC_PROMPT.format(context_text=context_text)
        return self.llm_provider.generate_completion([{"role": "user", "content": prompt}])

    def generate_faq(self, collection_id: str) -> str:
        context_text = self._assemble_collection_context(collection_id)
        prompt = FAQ_PROMPT.format(context_text=context_text)
        return self.llm_provider.generate_completion([{"role": "user", "content": prompt}])

    def generate_timeline(self, collection_id: str) -> str:
        context_text = self._assemble_collection_context(collection_id)
        prompt = TIMELINE_PROMPT.format(context_text=context_text)
        return self.llm_provider.generate_completion([{"role": "user", "content": prompt}])

    def generate_glossary(self, collection_id: str) -> str:
        context_text = self._assemble_collection_context(collection_id)
        prompt = GLOSSARY_PROMPT.format(context_text=context_text)
        return self.llm_provider.generate_completion([{"role": "user", "content": prompt}])

    def generate_flashcards(self, collection_id: str) -> List[Dict[str, str]]:
        context_text = self._assemble_collection_context(collection_id)
        prompt = FLASHCARDS_PROMPT.format(context_text=context_text)
        response = self.llm_provider.generate_completion([{"role": "user", "content": prompt}])
        data = parse_json_from_llm(response)
        if isinstance(data, list):
            return [{"question": str(x.get("question", "")), "answer": str(x.get("answer", ""))} for x in data if isinstance(x, dict)]
        return []
