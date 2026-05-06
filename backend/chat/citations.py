"""Service for extracting and validating citations from LLM output."""
from __future__ import annotations

import logging
import re
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)


class CitationService:
    """Service for managing citations in generated answers."""

    # Pattern to match [Source N] or [Source UUID]
    CITATION_PATTERN = re.compile(r'\[Source\s+([^\]]+)\]')

    def extract_citations(self, text: str) -> List[str]:
        """
        Extract citation labels from text.

        Args:
            text: The text to parse

        Returns:
            List of extracted labels (e.g., ["1", "2", "uuid-abc"])
        """
        matches = self.CITATION_PATTERN.findall(text)
        # Deduplicate while preserving order
        seen = set()
        unique_citations = []
        for match in matches:
            val = match.strip()
            if val not in seen:
                seen.add(val)
                unique_citations.append(val)
        return unique_citations

    def map_citations_to_chunks(
        self, 
        citation_labels: List[str], 
        retrieved_chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Map citation labels back to retrieved chunk metadata.

        Args:
            citation_labels: Labels extracted from the text
            retrieved_chunks: Original chunks used for context

        Returns:
            List of valid citation metadata objects
        """
        valid_citations = []
        
        for label in citation_labels:
            # 1. Try mapping as 1-based index (e.g., "[Source 1]")
            if label.isdigit():
                index = int(label) - 1
                if 0 <= index < len(retrieved_chunks):
                    chunk = retrieved_chunks[index]
                    valid_citations.append(self._format_citation(chunk))
                    continue
            
            # 2. Try mapping as chunk_id (e.g., "[Source uuid-abc]")
            for chunk in retrieved_chunks:
                if chunk['chunk_id'] == label:
                    valid_citations.append(self._format_citation(chunk))
                    break
        
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
