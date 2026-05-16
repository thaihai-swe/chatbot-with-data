"""Service for orchestrating streaming chat responses."""
from __future__ import annotations

import logging
import json
import uuid
import asyncio
from typing import Optional, Dict, Any, AsyncIterator

from chat.retrieval import AdvancedRetrievalService
from chat.context import ContextService
from chat.generation import GenerationService
from chat.citations import CitationService
from chat.grounding import GroundingService, get_grounding_service
from chat.safety import SafetyService, get_safety_service
from repositories.chat_repository import ChatRepository
from schemas.chat import AdvancedRetrievalConfig, SafetyTrace

logger = logging.getLogger(__name__)


from chat.cancellation import is_cancelled, clear_cancellation

class StreamingOrchestrator:
    """Orchestrator for streaming chat generation with status updates."""

    def __init__(
        self,
        advanced_retrieval_service: AdvancedRetrievalService,
        context_service: ContextService,
        generation_service: GenerationService,
        citation_service: CitationService,
        grounding_service: GroundingService,
        safety_service: SafetyService,
    ):
        self.advanced_retrieval_service = advanced_retrieval_service
        self.context_service = context_service
        self.generation_service = generation_service
        self.citation_service = citation_service
        self.grounding_service = grounding_service
        self.safety_service = safety_service

    async def stream_turn(
        self,
        session_id: str,
        query_text: str,
        advanced_config: Optional[AdvancedRetrievalConfig] = None,
    ) -> AsyncIterator[str]:
        """
        Stream a chat turn as SSE events.

        Events:
        - status: Current stage (retrieving, generating, etc.)
        - token: Answer text tokens
        - citations: Final citation list
        - error: Error message
        - done: Signal completion
        """
        turn_id = str(uuid.uuid4())

        try:
            # 1. Status: Understanding query & checking safety
            yield self._format_sse("status", {"stage": "retrieving", "message": "Checking query safety...", "turn_id": turn_id})

            # 1a. Safety check (Query)
            safety_trace = self.safety_service.check_query(query_text)
            
            if not safety_trace.answerability.is_answerable:
                # Handle early safety refusal
                answer_text = safety_trace.answerability.refusal_reason or "I cannot answer this question due to safety concerns."
                ChatRepository.create_turn(
                    id=turn_id,
                    session_id=session_id,
                    query_text=query_text,
                    status="completed",
                    answer_text=answer_text,
                    safety_status=safety_trace.query_classification,
                    safety_risk_score=1.0 if safety_trace.injection_risk == "high" else 0.0,
                    safety_reason=safety_trace.classifier_reason,
                )
                yield self._format_sse("token", {"content": answer_text})
                yield self._format_sse("done", {"turn_id": turn_id})
                return

            # 2. Status: Retrieving
            yield self._format_sse("status", {"stage": "retrieving", "message": "Searching knowledge base...", "turn_id": turn_id})

            session = ChatRepository.get_session(session_id)
            if not session:
                yield self._format_sse("error", {"message": f"Session {session_id} not found"})
                return

            config = advanced_config if advanced_config is not None else AdvancedRetrievalConfig()

            # Retrieval
            retrieved_chunks, trace = self.advanced_retrieval_service.retrieve(
                query_text=query_text,
                config=config,
                collection_id=session.collection_id,
            )

            if is_cancelled(turn_id):
                yield self._format_sse("status", {"stage": "cancelled", "message": "Cancelled."})
                return

            # 3. Chunk safety check
            checked_chunks = self.safety_service.check_chunks(retrieved_chunks)
            safe_chunks = [c for c in checked_chunks if c.get("safety_risk") != "high"]
            
            if len(safe_chunks) < len(retrieved_chunks):
                logger.info(f"Filtered out {len(retrieved_chunks) - len(safe_chunks)} malicious chunks in stream.")

            # 4. Evaluate grounding
            is_sufficient, refusal_reason = self.grounding_service.evaluate_evidence(safe_chunks)

            # Update safety_trace with grounding info
            if not is_sufficient:
                safety_trace.answerability.is_answerable = False
                safety_trace.answerability.refusal_reason = refusal_reason
                safety_trace.groundedness.status = "unsupported"
            else:
                safety_trace.groundedness.status = "supported"
                safety_trace.groundedness.score = 1.0 

            # Create turn record
            history = ChatRepository.list_turns_by_session(session_id)
            context_package = self.context_service.assemble_context(
                query_text=query_text,
                retrieved_chunks=safe_chunks,
                chat_history=history,
            )

            ChatRepository.create_turn(
                id=turn_id,
                session_id=session_id,
                query_text=query_text,
                retrieved_chunks_json=json.dumps(safe_chunks),
                context_used_json=json.dumps(context_package),
                status="generating",
                safety_status=safety_trace.query_classification,
                safety_risk_score=1.0 if safety_trace.injection_risk == "high" else 0.0,
                safety_reason=safety_trace.classifier_reason,
            )

            if not is_sufficient:
                # 5. Handle refusal
                yield self._format_sse("status", {"stage": "generating", "message": "Formulating response..."})
                for token in refusal_reason.split():
                    if is_cancelled(turn_id):
                        ChatRepository.update_turn_status(turn_id, "cancelled")
                        yield self._format_sse("status", {"stage": "cancelled", "message": "Cancelled."})
                        return
                    yield self._format_sse("token", {"content": token + " "})
                    await asyncio.sleep(0.01)

                ChatRepository.update_turn_status(
                    turn_id=turn_id,
                    status="completed",
                    answer_text=refusal_reason,
                )
                yield self._format_sse("done", {"turn_id": turn_id})
                return

            # 6. Status: Generating
            yield self._format_sse("status", {"stage": "generating", "message": "Generating answer..."})

            full_answer = ""
            # Generation stream
            for token in self.generation_service.generate_answer(context_package, stream=True):
                if is_cancelled(turn_id):
                    ChatRepository.update_turn_status(turn_id, "cancelled")
                    yield self._format_sse("status", {"stage": "cancelled", "message": "Cancelled."})
                    return
                full_answer += token
                yield self._format_sse("token", {"content": token})

            # 7. Status: Finalizing citations
            yield self._format_sse("status", {"stage": "finalizing", "message": "Finalizing citations..."})

            if is_cancelled(turn_id):
                ChatRepository.update_turn_status(turn_id, "cancelled")
                yield self._format_sse("status", {"stage": "cancelled", "message": "Cancelled."})
                return

            citation_labels = self.citation_service.extract_citations(full_answer)
            valid_citations = self.citation_service.map_citations_to_chunks(
                citation_labels, safe_chunks
            )

            citation_objects = []
            for cit_data in valid_citations:
                cit = ChatRepository.create_citation(
                    id=str(uuid.uuid4()),
                    turn_id=turn_id,
                    chunk_id=cit_data['chunk_id'],
                    document_id=cit_data['document_id'],
                    metadata_json=json.dumps(cit_data),
                )
                citation_objects.append({
                    "id": cit.id,
                    "chunk_id": cit.chunk_id,
                    "document_id": cit.document_id,
                    "metadata": cit_data,
                })

            ChatRepository.update_turn_status(
                turn_id=turn_id,
                status="completed",
                answer_text=full_answer,
            )

            # Include safety trace and retrieval trace in the final citations event or a separate event
            yield self._format_sse("citations", {
                "citations": citation_objects,
                "retrieval_trace": trace.dict() if hasattr(trace, 'dict') else trace,
                "safety_trace": safety_trace.dict() if hasattr(safety_trace, 'dict') else safety_trace
            })
            yield self._format_sse("done", {"turn_id": turn_id})

        except Exception as e:
            logger.error(f"Streaming error for turn {turn_id}: {str(e)}")
            ChatRepository.update_turn_status(
                turn_id=turn_id,
                status="error",
                error_message=str(e),
            )
            yield self._format_sse("error", {"message": str(e)})
        finally:
            clear_cancellation(turn_id)

    def _format_sse(self, event: str, data: Dict[str, Any]) -> str:
        """Format data as an SSE event string."""
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"


from fastapi import Depends
from chat.context import get_context_service
from chat.generation import get_generation_service
from chat.citations import get_citation_service
from chat.retrieval import get_advanced_retrieval_service

def get_streaming_orchestrator(
    advanced_retrieval_service: AdvancedRetrievalService = Depends(get_advanced_retrieval_service),
    context_service: ContextService = Depends(get_context_service),
    generation_service: GenerationService = Depends(get_generation_service),
    citation_service: CitationService = Depends(get_citation_service),
    grounding_service: GroundingService = Depends(get_grounding_service),
    safety_service: SafetyService = Depends(get_safety_service),
) -> StreamingOrchestrator:
    """Factory function for StreamingOrchestrator."""
    return StreamingOrchestrator(
        advanced_retrieval_service,
        context_service,
        generation_service,
        citation_service,
        grounding_service,
        safety_service,
    )
