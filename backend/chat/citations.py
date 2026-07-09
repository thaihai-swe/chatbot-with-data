"""Service for extracting and validating citations from LLM output."""
from __future__ import annotations

import logging
import re
from typing import List, Dict, Any, Optional

from chat.prompts import QUOTE_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)

_SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+')
_PARAGRAPH_SPLIT_RE = re.compile(r'\n{2,}')


def split_paragraphs(text: str) -> List[Dict[str, Any]]:
    """Split answer text into paragraph blocks by blank lines.

    Returns list of {text, start, end} where start/end are char offsets
    into the original text. Empty paragraphs are skipped.
    """
    if not text:
        return []
    blocks: List[Dict[str, Any]] = []
    last_end = 0
    for match in _PARAGRAPH_SPLIT_RE.finditer(text):
        chunk = text[last_end:match.start()]
        stripped = chunk.strip()
        if stripped:
            # Adjust start/end to the stripped span within original
            lead = len(chunk) - len(chunk.lstrip())
            trail = len(chunk) - len(chunk.rstrip())
            start = last_end + lead
            end = match.start() - trail
            blocks.append({"text": stripped, "start": start, "end": end})
        last_end = match.end()
    # Tail after last blank-line separator
    chunk = text[last_end:]
    stripped = chunk.strip()
    if stripped:
        lead = len(chunk) - len(chunk.lstrip())
        trail = len(chunk) - len(chunk.rstrip())
        start = last_end + lead
        end = len(text) - trail
        blocks.append({"text": stripped, "start": start, "end": end})
    return blocks


class CitationService:
    """Service for managing citations in generated answers."""

    # Pattern to match [Source N], [Source UUID], or [N]
    CITATION_PATTERN = re.compile(r'\[Source\s+([^\]]+)\]|\[(\d+)\]')

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
        matches = self.CITATION_PATTERN.finditer(text)
        seen = set()
        unique_citations = []
        for match in matches:
            val = match.group(1) or match.group(2)
            if val:
                val = val.strip()
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
            if f"[Source {label}]" in sentence or f"[{label}]" in sentence:
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

    def _jaccard_quote(self, claim_text: str, chunk_text: str) -> Dict[str, Any]:
        """Extract best Jaccard quote from chunk for a claim.
        Returns {quote_text, match_score, match_method}.
        No LLM fallback — Jaccard only.
        """
        claim_words = set(claim_text.lower().split())
        best_score = 0.0
        best_sentence = ""
        for sentence in _SENTENCE_SPLIT_RE.split(chunk_text):
            sentence_stripped = sentence.strip()
            if not sentence_stripped:
                continue
            chunk_words = set(sentence_stripped.lower().split())
            if not chunk_words:
                continue
            inter = claim_words & chunk_words
            union = claim_words | chunk_words
            score = len(inter) / len(union) if union else 0.0
            if score > best_score:
                best_score = score
                best_sentence = sentence_stripped
        return {
            "quote_text": best_sentence if best_score >= self.QUOTE_MATCH_THRESHOLD else "",
            "match_score": best_score,
            "match_method": "jaccard",
        }

    def build_provenance(
        self,
        answer_text: str,
        retrieved_chunks: List[Dict[str, Any]],
        llm_provider: Any = None,  # unused — Jaccard only
    ) -> Dict[str, Any]:
        """
        Build claim-level provenance graph from answer text.

        Args:
            answer_text: Full generated answer
            retrieved_chunks: List of chunk metadata used in context
            llm_provider: Optional (unused in v1 — Jaccard only)

        Returns:
            Dict with keys:
              claims: list of ClaimItem dicts
              coverage: ProvenanceCoverage dict
        """
        paragraphs = split_paragraphs(answer_text)
        claims: List[Dict[str, Any]] = []
        for idx, para in enumerate(paragraphs):
            labels = self.extract_citations(para["text"])
            mapped = self.map_citations_to_chunks(
                labels, retrieved_chunks, answer_text=para["text"], llm_provider=llm_provider
            )
            chunk_ids = [c["chunk_id"] for c in mapped]
            # Use first citation's quote/score/method if any
            quote_text = ""
            match_score = None
            match_method = None
            if mapped:
                q = mapped[0].get("quote_text")
                if q:
                    quote_text = q
                # We don't store score/method from map_citations_to_chunks currently;
                # we could add it there. For now, use Jaccard on the paragraph level.
                j = self._jaccard_quote(para["text"], " ".join(
                    c.get("text") or c.get("content") or "" for c in mapped
                ))
                match_score = j["match_score"]
                match_method = j["match_method"]
            claims.append({
                "index": idx,
                "text": para["text"],
                "start": para["start"],
                "end": para["end"],
                "labels": labels,
                "chunks": chunk_ids,
                "cited": len(chunk_ids) > 0,
                "quote_text": quote_text or None,
                "match_score": match_score,
                "match_method": match_method,
            })
        cited = sum(1 for c in claims if c["cited"])
        total = len(claims)
        uncited = [i for i, c in enumerate(claims) if not c["cited"]]
        coverage = {"cited": cited, "total": total, "uncited_indices": uncited}
        return {"claims": claims, "coverage": coverage}


def finalize_turn(
    answer_text: str,
    retrieved_chunks: List[Dict[str, Any]],
    context_package: Dict[str, Any],
    llm_provider: Any,
    grounding_service: Any,
    chat_repository: Any,
    turn_id: str,
    conflict_service: Any = None,
) -> Dict[str, Any]:
    """
    Shared finalize logic for sync and stream paths.

    Computes provenance, groundedness, persists citations and turn update.
    Returns dict ready for SSE citations event payload.
    """
    import json
    import uuid
    from chat.conflict import ConflictDetectionService

    def _safe(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: _safe(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_safe(v) for v in obj]
        if hasattr(obj, "item"):
            return obj.item()
        return obj

    citation_service = CitationService()

    # 1. Build provenance
    provenance = citation_service.build_provenance(answer_text, retrieved_chunks, llm_provider)

    # 2. Groundedness score
    score, reason = grounding_service.calculate_groundedness(answer_text, retrieved_chunks)

    # 3. Persist citations (per label, like before)
    citation_labels = citation_service.extract_citations(answer_text)
    valid_citations = citation_service.map_citations_to_chunks(
        citation_labels, retrieved_chunks, answer_text=answer_text, llm_provider=llm_provider
    )

    citation_objects = []
    for cit_data in valid_citations:
        cit = chat_repository.create_citation(
            id=str(uuid.uuid4()),
            turn_id=turn_id,
            chunk_id=cit_data['chunk_id'],
            document_id=cit_data['document_id'],
            quote_text=cit_data.get('quote_text'),
            metadata_json=json.dumps(_safe(cit_data)),
        )
        citation_objects.append({
            "id": cit.id,
            "chunk_id": cit.chunk_id,
            "document_id": cit.document_id,
            "quote_text": cit_data.get('quote_text'),
            "metadata": cit_data,
        })

    # 4. Conflict status
    conflict_status = "no_conflict"
    conflict_details = None
    unique_doc_ids = {chunk.get("document_id") for chunk in retrieved_chunks if chunk.get("document_id")}
    if len(unique_doc_ids) > 1:
        svc = conflict_service or ConflictDetectionService(llm_provider)
        conflict_res = svc.detect_conflict(answer_text, retrieved_chunks)
        if conflict_res.get("has_conflict"):
            if conflict_res.get("surfaced_correctly"):
                conflict_status = "resolved_conflict"
            else:
                conflict_status = "unresolved_conflict"
            conflict_details = conflict_res.get("conflict_details")

    # 5. Update turn with provenance_json, groundedness, context_used
    context_package["conflict_status"] = conflict_status
    context_package["conflict_details"] = conflict_details
    chat_repository.update_turn_status(
        turn_id=turn_id,
        status="completed",
        answer_text=answer_text,
        groundedness_score=score,
        context_used_json=json.dumps(_safe(context_package)),
        provenance_json=json.dumps(_safe(provenance)),
    )

    return {
        "provenance": provenance,
        "citations": citation_objects,
        "groundedness_score": score,
        "groundedness_reason": reason,
        "conflict_status": conflict_status,
        "conflict_details": conflict_details,
    }


def get_citation_service() -> CitationService:
    """Factory function for CitationService."""
    return CitationService()
