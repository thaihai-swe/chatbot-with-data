"""Service for orchestrating streaming chat responses."""
from __future__ import annotations

import logging
import json
import uuid
import asyncio
from typing import Optional, List, Dict, Any, AsyncIterator

from chat.retrieval import RetrievalService
from chat.context import ContextService
from chat.generation import GenerationService
from chat.citations import CitationService
from chat.grounding import GroundingService
from repositories.chat_repository import ChatRepository

logger = logging.getLogger(__name__)


from chat.cancellation import is_cancelled, clear_cancellation

class StreamingOrchestrator:
    """Orchestrator for streaming chat generation with status updates."""

    def __init__(
        self,
        retrieval_service: RetrievalService,
        context_service: ContextService,
        generation_service: GenerationService,
        citation_service: CitationService,
        grounding_service: GroundingService,
    ):
        self.retrieval_service = retrieval_service
        self.context_service = context_service
        self.generation_service = generation_service
        self.citation_service = citation_service
        self.grounding_service = grounding_service

    async def stream_turn(
        self,
        session_id: str,
        query_text: str,
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
            # 1. Status: Understanding query & retrieving
            yield self._format_sse("status", {"stage": "retrieving", "message": "Searching knowledge base...", "turn_id": turn_id})
            
            session = ChatRepository.get_session(session_id)
            if not session:
                yield self._format_sse("error", {"message": f"Session {session_id} not found"})
                return

            # Retrieval
            retrieved_chunks = self.retrieval_service.retrieve_relevant_chunks(
                query_text=query_text,
                collection_id=session.collection_id,
            )

            if is_cancelled(turn_id):
                yield self._format_sse("status", {"stage": "cancelled", "message": "Cancelled."})
                return

            # 2. Evaluate grounding
            is_sufficient, refusal_reason = self.grounding_service.evaluate_evidence(retrieved_chunks)
            
            # Create turn record
            history = ChatRepository.list_turns_by_session(session_id)
            context_package = self.context_service.assemble_context(
                query_text=query_text,
                retrieved_chunks=retrieved_chunks,
                chat_history=history,
            )
            
            ChatRepository.create_turn(
                id=turn_id,
                session_id=session_id,
                query_text=query_text,
                retrieved_chunks_json=json.dumps(retrieved_chunks),
                context_used_json=json.dumps(context_package),
                status="generating",
            )

            if not is_sufficient:
                # 3. Handle refusal
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

            # 4. Status: Generating
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
                await asyncio.sleep(0)

            # 5. Status: Finalizing citations
            yield self._format_sse("status", {"stage": "finalizing", "message": "Finalizing citations..."})
            
            if is_cancelled(turn_id):
                ChatRepository.update_turn_status(turn_id, "cancelled")
                yield self._format_sse("status", {"stage": "cancelled", "message": "Cancelled."})
                return

            citation_labels = self.citation_service.extract_citations(full_answer)
            valid_citations = self.citation_service.map_citations_to_chunks(
                citation_labels, retrieved_chunks
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
            
            yield self._format_sse("citations", {"citations": citation_objects})
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
from chat.retrieval import get_retrieval_service
from chat.context import get_context_service
from chat.generation import get_generation_service
from chat.citations import get_citation_service
from chat.grounding import get_grounding_service

def get_streaming_orchestrator(
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    context_service: ContextService = Depends(get_context_service),
    generation_service: GenerationService = Depends(get_generation_service),
    citation_service: CitationService = Depends(get_citation_service),
    grounding_service: GroundingService = Depends(get_grounding_service),
) -> StreamingOrchestrator:
    """Factory function for StreamingOrchestrator."""
    return StreamingOrchestrator(
        retrieval_service,
        context_service,
        generation_service,
        citation_service,
        grounding_service,
    )
