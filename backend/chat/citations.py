"""Service for extracting and validating citations from LLM output."""
from __future__ import annotations

import logging
import re
from typing import List, Dict, Any, Optional

from chat.prompts import QUOTE_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)

_SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+|\n+')
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
    # Merge trailing citation-only blocks backward
    merged_blocks: List[Dict[str, Any]] = []
    for block in blocks:
        # Check if the block consists only of [Source ...] citations and whitespace
        is_only_citation = bool(re.match(r"^(\[Source\s+[^\]]+\]|\s)*$", block["text"]))
        if is_only_citation and merged_blocks:
            merged_blocks[-1]["text"] += "\n\n" + block["text"]
            merged_blocks[-1]["end"] = block["end"]
        else:
            merged_blocks.append(block)

    return merged_blocks


class CitationService:
    """Service for managing citations in generated answers."""

    # Pattern to match [Source <uuid>] (UUID format) or legacy [Source N] / [N]
    # UUID format: 8-4-4-4-12 hex digits (e.g., abc-123-def-ghi-jkl)
    # The pattern ignores any text after the UUID inside the brackets
    UUID_PATTERN = re.compile(r'\[Source\s+([a-f0-9-]{36})(?:[^\]]*)\]')
    LEGACY_PATTERN = re.compile(r'\[Source\s+(\d+)\]|\[(\d+)\]')
    # Combined pattern for extraction
    CITATION_PATTERN = re.compile(r'\[Source\s+([^\]]+)\]|\[(\d+)\]')

    # Jaccard similarity threshold for sentence overlap matching
    QUOTE_MATCH_THRESHOLD = 0.35

    def extract_citations(self, text: str) -> List[str]:
        """
        Extract citation labels from text.

        Prefers UUID format [Source abc-123-def] over legacy numeric [Source 1].

        Args:
            text: The text to parse

        Returns:
            List of extracted labels (UUIDs preferred, legacy numeric as fallback)
        """
        # First try UUID format
        uuid_matches = self.UUID_PATTERN.findall(text)
        if uuid_matches:
            # Remove duplicates while preserving order
            seen = set()
            unique_citations = []
            for val in uuid_matches:
                val = val.strip()
                if val not in seen:
                    seen.add(val)
                    unique_citations.append(val)
            return unique_citations

        # Fallback to legacy numeric format
        matches = self.LEGACY_PATTERN.finditer(text)
        seen = set()
        unique_citations = []
        for match in matches:
            val = match.group(1) or match.group(2)
            if val:
                val = val.strip()
                if val not in seen:
                    seen.add(val)
                    unique_citations.append(val)
        if unique_citations:
            logger.warning("Legacy numeric citation format detected. Consider updating to UUID format [Source <chunk_id>].")
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
            min_len = min(len(claim_words), len(chunk_words))
            score = len(intersection) / min_len if min_len > 0 else 0.0

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
            "chunk_id": chunk.get('chunk_id', ''),
            "document_id": chunk.get('document_id', ''),
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
            # Use overlap coefficient to handle paragraph vs sentence length discrepancy
            min_len = min(len(claim_words), len(chunk_words))
            score = len(inter) / min_len if min_len > 0 else 0.0
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
            # IMPLICIT PROVENANCE: If LLM failed to cite, try to find a Jaccard match anyway!
            if not mapped and len(para["text"].strip()) > 10:
                best_score = -1.0
                best_chunk = None
                for chunk in retrieved_chunks:
                    chunk_text = chunk.get("text") or chunk.get("content") or ""
                    j = self._jaccard_quote(para["text"], chunk_text)
                    if j["match_score"] > best_score:
                        best_score = j["match_score"]
                        best_chunk = chunk
                
                if best_score >= self.QUOTE_MATCH_THRESHOLD and best_chunk:
                    chunk_id = best_chunk.get("chunk_id")
                    if chunk_id:
                        cit = self._format_citation(best_chunk)
                        mapped = [cit]
                        # Inject the missing citation into the text so frontend renders a pill
                        para["text"] += f" [Source {chunk_id}]"
                        labels.append(chunk_id)

            chunk_ids = [c["chunk_id"] for c in mapped]
            # Use first citation's quote/score/method if any
            quote_text = ""
            match_score = 0.0
            match_method = "none"
            matched_chunk_id = None
            
            if mapped:
                q = mapped[0].get("quote_text")
                if q:
                    quote_text = q
                
                best_score = -1.0
                best_chunk_id = None
                
                for c in mapped:
                    # c is from _format_citation, so it lacks 'text'. Find original chunk.
                    orig_chunk = next((rc for rc in retrieved_chunks if rc["chunk_id"] == c["chunk_id"]), {})
                    chunk_text = orig_chunk.get("text") or orig_chunk.get("content") or ""
                    j = self._jaccard_quote(para["text"], chunk_text)
                    if j["match_score"] > best_score:
                        best_score = j["match_score"]
                        best_chunk_id = c.get("chunk_id")
                
                match_score = best_score if best_score >= 0 else 0.0
                match_method = "jaccard"
                matched_chunk_id = best_chunk_id
                
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
                "matched_chunk_id": matched_chunk_id,
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
