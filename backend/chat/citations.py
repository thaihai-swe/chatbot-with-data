"""Service for extracting and validating citations from LLM output."""
from __future__ import annotations

import logging
import re
from typing import List, Dict, Any, Optional

from chat.prompts import QUOTE_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)

_SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+')


class CitationService:
    """Service for managing citations in generated answers."""

    # Pattern to match [Source N] or [Source UUID]
    CITATION_PATTERN = re.compile(r'\[Source\s+([^\]]+)\]')

    # Jaccard similarity threshold for sentence overlap matching
    QUOTE_MATCH_THRESHOLD = 0.5

    def extract_citations(self, text: str) -> List[str]:
        """
        Extract citation labels from text.

        Args:
            text: The text to parse

        Returns:
            List of extracted labels (e.g., ["1", "2", "uuid-abc"])
        """
        matches = self.CITATION_PATTERN.findall(text)
        seen = set()
        unique_citations = []
        for match in matches:
            val = match.strip()
            if val not in seen:
                seen.add(val)
                unique_citations.append(val)
        return unique_citations

    def extract_quote(
        self,
        chunk_text: str,
        answer_text: str,
        label: str,
        llm_provider: Any = None,
    ) -> str:
        """
        Extract the exact sentence(s) from chunk_text cited by [Source {label}].

        Uses sentence-level Jaccard word overlap matching first.
        Falls back to LLM extraction when no sentence meets the threshold.

        Args:
            chunk_text: The full text of the source chunk
            answer_text: The full generated answer containing [Source {label}]
            label: The citation label (e.g., "1", "2", "uuid-abc")
            llm_provider: Optional LLM provider for fallback extraction

        Returns:
            The extracted quote string, or "" if no match found
        """
        answer_sentences = _SENTENCE_SPLIT_RE.split(answer_text)
        claim_sentence = ""
        for sentence in answer_sentences:
            if f"[Source {label}]" in sentence:
                claim_sentence = sentence.strip()
                break

        if not claim_sentence:
            return ""

        chunk_sentences = _SENTENCE_SPLIT_RE.split(chunk_text)
        best_score = 0.0
        best_sentence = ""

        claim_words = set(claim_sentence.lower().split())

        for sentence in chunk_sentences:
            sentence_stripped = sentence.strip()
            if not sentence_stripped:
                continue
            chunk_words = set(sentence_stripped.lower().split())
            if not chunk_words:
                continue
            intersection = claim_words & chunk_words
            union = claim_words | chunk_words
            score = len(intersection) / len(union) if union else 0.0

            if score > best_score:
                best_score = score
                best_sentence = sentence_stripped

        if best_score >= self.QUOTE_MATCH_THRESHOLD:
            return best_sentence

        if llm_provider is not None:
            try:
                prompt = QUOTE_EXTRACTION_PROMPT.format(
                    claim_sentence=claim_sentence,
                    chunk_text=chunk_text,
                )
                response = llm_provider.generate_completion(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                )
                result = response.strip().strip('"').strip("'")
                return result if result else ""
            except Exception as e:
                logger.warning(f"LLM quote extraction failed for label [{label}]: {e}")
                return ""

        return ""

    def map_citations_to_chunks(
        self,
        citation_labels: List[str],
        retrieved_chunks: List[Dict[str, Any]],
        answer_text: Optional[str] = None,
        llm_provider: Any = None,
    ) -> List[Dict[str, Any]]:
        """
        Map citation labels back to retrieved chunk metadata.

        When answer_text is provided, also extracts quote_text for each citation.

        Args:
            citation_labels: Labels extracted from the text
            retrieved_chunks: Original chunks used for context
            answer_text: Full generated answer (required for quote extraction)
            llm_provider: Optional LLM provider for fallback quote extraction

        Returns:
            List of valid citation metadata objects with quote_text
        """
        valid_citations = []

        for label in citation_labels:
            chunk = None
            if label.isdigit():
                index = int(label) - 1
                if 0 <= index < len(retrieved_chunks):
                    chunk = retrieved_chunks[index]

            if chunk is None:
                for c in retrieved_chunks:
                    if c['chunk_id'] == label:
                        chunk = c
                        break

            if chunk is None:
                continue

            citation = self._format_citation(chunk)

            if answer_text is not None:
                chunk_text = chunk.get("text") or chunk.get("content") or ""
                citation["quote_text"] = self.extract_quote(
                    chunk_text=chunk_text,
                    answer_text=answer_text,
                    label=label,
                    llm_provider=llm_provider,
                )

            valid_citations.append(citation)

        return valid_citations

    def _format_citation(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Format a chunk into a citation metadata object."""
        return {
            "chunk_id": chunk['chunk_id'],
            "document_id": chunk['document_id'],
            "title": chunk.get('title'),
            "page_number": chunk.get('page_number'),
            "section_title": chunk.get('section_title'),
            "source_url": chunk.get('source_url'),
        }


def get_citation_service() -> CitationService:
    """Factory function for CitationService."""
    return CitationService()
