"""Orchestration service for chat workflows."""
from __future__ import annotations

import logging
import json
import uuid
from typing import Optional

from fastapi import Depends

from chat.retrieval import AdvancedRetrievalService, get_advanced_retrieval_service
from chat.context import ContextService, get_context_service
from chat.generation import GenerationService, get_generation_service
from chat.citations import CitationService, get_citation_service
from chat.grounding import GroundingService, get_grounding_service
from chat.safety import SafetyService, get_safety_service
from repositories.chat_repository import ChatRepository
from schemas.chat import ChatTurnResponse, CitationResponse, AdvancedRetrievalConfig, SafetyTrace
from config import get_config, get_settings_manager

logger = logging.getLogger(__name__)


class ChatService:
    """High-level service coordinating chat retrieval and generation."""

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

    def process_turn(
        self,
        session_id: str,
        query_text: str,
        advanced_config: Optional[AdvancedRetrievalConfig] = None,
    ) -> ChatTurnResponse:
        """
        Process a chat turn: retrieve, evaluate, generate, and persist.
        """
        # 1. Get session
        session = ChatRepository.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # 1.1 Capture run snapshot
        turn_id = str(uuid.uuid4())
        get_settings_manager().save_run_snapshot(turn_id, domain="chat")

        # 2. Safety check (Query)
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
            turn = ChatRepository.get_turn(turn_id)
            return ChatTurnResponse(
                id=turn.id,
                session_id=turn.session_id,
                query_text=turn.query_text,
                answer_text=turn.answer_text,
                retrieved_chunks_json=turn.retrieved_chunks_json,
                context_used_json=turn.context_used_json,
                status=turn.status,
                safety_status=turn.safety_status,
                safety_risk_score=turn.safety_risk_score,
                safety_reason=turn.safety_reason,
                groundedness_score=turn.groundedness_score,
                error_message=turn.error_message,
                created_at=turn.created_at,
                updated_at=turn.updated_at,
                citations=[],
                retrieval_trace=None,
                safety_trace=safety_trace,
            )

        # 3. Retrieve chunks
        if advanced_config is None:
            advanced_config = AdvancedRetrievalConfig()
            
        retrieved_chunks, trace = self.advanced_retrieval_service.retrieve(
            query_text=query_text,
            config=advanced_config,
            collection_ids=session.collection_ids,
        )

        # 4. Chunk safety check
        checked_chunks = self.safety_service.check_chunks(retrieved_chunks)
        safe_chunks = [c for c in checked_chunks if c.get("safety_risk") != "high"]
        
        if len(safe_chunks) < len(retrieved_chunks):
            logger.info(f"Filtered out {len(retrieved_chunks) - len(safe_chunks)} malicious chunks.")

        # 5. Evaluate evidence
        is_sufficient, refusal_reason = self.grounding_service.evaluate_evidence(safe_chunks)
        
        # Update safety_trace with grounding info
        if not is_sufficient:
            safety_trace.answerability.is_answerable = False
            safety_trace.answerability.refusal_reason = refusal_reason
            safety_trace.groundedness.status = "unsupported"
        else:
            safety_trace.groundedness.status = "supported"
            # We could compute a real score here if GroundingService supported it
            safety_trace.groundedness.score = 1.0 

        # 6. Create turn record (pending)
        # turn_id was pre-generated for snapshot
        history = ChatRepository.list_turns_by_session(session_id)

        context_package = self.context_service.assemble_context(
            query_text=query_text,
            retrieved_chunks=safe_chunks,
            chat_history=history,
        )

        turn = ChatRepository.create_turn(
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

        try:
            if not is_sufficient:
                # Handle grounding refusal
                answer_text = refusal_reason
                ChatRepository.update_turn_status(
                    turn_id=turn_id,
                    status="completed",
                    answer_text=answer_text,
                )
                valid_citations = []
            else:
                # 5. Generate answer - force stream=False for non-streaming response
                answer_text = self.generation_service.generate_answer(context_package, stream=False)

                # 5.1 Calculate real groundedness for observability
                score, reason = self.grounding_service.calculate_groundedness(
                    answer_text, 
                    safe_chunks
                )
                safety_trace.groundedness.score = score
                safety_trace.groundedness.status = "supported" if score >= 0.7 else "partial"

                # 6. Extract and validate citations
                citation_labels = self.citation_service.extract_citations(answer_text)
                valid_citations = self.citation_service.map_citations_to_chunks(
                    citation_labels, safe_chunks
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
                    groundedness_score=score,  # Persist score
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
                safety_status=turn.safety_status,
                safety_risk_score=turn.safety_risk_score,
                safety_reason=turn.safety_reason,
                groundedness_score=turn.groundedness_score,
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
                retrieval_trace=trace,
                safety_trace=safety_trace,
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
    advanced_retrieval_service: AdvancedRetrievalService = Depends(get_advanced_retrieval_service),
    context_service: ContextService = Depends(get_context_service),
    generation_service: GenerationService = Depends(get_generation_service),
    citation_service: CitationService = Depends(get_citation_service),
    grounding_service: GroundingService = Depends(get_grounding_service),
    safety_service: SafetyService = Depends(get_safety_service),
) -> ChatService:
    """Factory function for ChatService."""
    return ChatService(
        advanced_retrieval_service,
        context_service,
        generation_service,
        citation_service,
        grounding_service,
        safety_service,
    )
