"""Orchestration service for chat workflows."""
from __future__ import annotations

import logging
import json
import uuid
from typing import Optional, List, Dict, Any

from chat.retrieval import RetrievalService, get_retrieval_service
from chat.context import ContextService, get_context_service
from chat.generation import GenerationService, get_generation_service
from chat.citations import CitationService, get_citation_service
from chat.grounding import GroundingService, get_grounding_service
from repositories.chat_repository import ChatRepository
from schemas.chat import ChatTurnResponse, CitationResponse

logger = logging.getLogger(__name__)


class ChatService:
    """High-level service coordinating chat retrieval and generation."""

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

    def process_turn(
        self,
        session_id: str,
        query_text: str,
    ) -> ChatTurnResponse:
        """
        Process a chat turn: retrieve, evaluate, generate, and persist.
        """
        # 1. Get session
        session = ChatRepository.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # 2. Retrieve chunks
        retrieved_chunks = self.retrieval_service.retrieve_relevant_chunks(
            query_text=query_text,
            collection_id=session.collection_id,
        )

        # 3. Evaluate evidence
        is_sufficient, refusal_reason = self.grounding_service.evaluate_evidence(retrieved_chunks)
        
        # 4. Create turn record (pending)
        turn_id = str(uuid.uuid4())
        history = ChatRepository.list_turns_by_session(session_id)
        
        context_package = self.context_service.assemble_context(
            query_text=query_text,
            retrieved_chunks=retrieved_chunks,
            chat_history=history,
        )
        
        turn = ChatRepository.create_turn(
            id=turn_id,
            session_id=session_id,
            query_text=query_text,
            retrieved_chunks_json=json.dumps(retrieved_chunks),
            context_used_json=json.dumps(context_package),
            status="generating",
        )

        try:
            if not is_sufficient:
                # Handle refusal case
                answer_text = refusal_reason
                ChatRepository.update_turn_status(
                    turn_id=turn_id,
                    status="completed",
                    answer_text=answer_text,
                )
                valid_citations = []
            else:
                # 5. Generate answer
                answer_text = self.generation_service.generate_answer(context_package)
                
                # 6. Extract and validate citations
                citation_labels = self.citation_service.extract_citations(answer_text)
                valid_citations = self.citation_service.map_citations_to_chunks(
                    citation_labels, retrieved_chunks
                )
                
                # 7. Persist citations and update turn
                for cit_data in valid_citations:
                    ChatRepository.create_citation(
                        id=str(uuid.uuid4()),
                        turn_id=turn_id,
                        chunk_id=cit_data['chunk_id'],
                        document_id=cit_data['document_id'],
                        metadata_json=json.dumps(cit_data),
                    )
                
                ChatRepository.update_turn_status(
                    turn_id=turn_id,
                    status="completed",
                    answer_text=answer_text,
                )

            # 8. Reload turn and return
            turn = ChatRepository.get_turn(turn_id)
            citations = ChatRepository.list_citations_by_turn(turn_id)
            
            return ChatTurnResponse(
                id=turn.id,
                session_id=turn.session_id,
                query_text=turn.query_text,
                answer_text=turn.answer_text,
                retrieved_chunks_json=turn.retrieved_chunks_json,
                context_used_json=turn.context_used_json,
                status=turn.status,
                error_message=turn.error_message,
                created_at=turn.created_at,
                updated_at=turn.updated_at,
                citations=[
                    CitationResponse(
                        id=c.id,
                        turn_id=c.turn_id,
                        chunk_id=c.chunk_id,
                        document_id=c.document_id,
                        quote_text=c.quote_text,
                        metadata_json=c.metadata_json,
                        created_at=c.created_at,
                    )
                    for c in citations
                ],
            )

        except Exception as e:
            logger.error(f"Error processing turn {turn_id}: {str(e)}")
            ChatRepository.update_turn_status(
                turn_id=turn_id,
                status="error",
                error_message=str(e),
            )
            raise


def get_chat_service(
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    context_service: ContextService = Depends(get_context_service),
    generation_service: GenerationService = Depends(get_generation_service),
    citation_service: CitationService = Depends(get_citation_service),
    grounding_service: GroundingService = Depends(get_grounding_service),
) -> ChatService:
    """Factory function for ChatService."""
    return ChatService(
        retrieval_service,
        context_service,
        generation_service,
        citation_service,
        grounding_service,
    )
