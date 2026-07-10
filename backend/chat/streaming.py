"""Service for orchestrating streaming chat responses."""
from __future__ import annotations

import logging
import json
import uuid
import asyncio
from typing import Optional, Dict, Any, AsyncIterator


def _json_safe(obj: Any) -> Any:
    """Recursively convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    elif hasattr(obj, "item"):  # numpy scalars (float32, float64, int64, etc.)
        return obj.item()
    return obj

from chat.advanced_retrieval import AdvancedRetrievalService
from chat.context import ContextService, load_chunk_notes
from chat.generation import GenerationService
from chat.citations import CitationService, finalize_turn
from chat.grounding import GroundingService, get_grounding_service
from chat.safety import SafetyService, get_safety_service
from repositories.chat_repository import ChatRepository
from schemas.chat import SafetyTrace
from config import get_config

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
        conflict_service: Optional[ConflictDetectionService] = None,
    ):
        self.advanced_retrieval_service = advanced_retrieval_service
        self.context_service = context_service
        self.generation_service = generation_service
        self.citation_service = citation_service
        self.grounding_service = grounding_service
        self.safety_service = safety_service
        if conflict_service is None:
            from chat.conflict import ConflictDetectionService
            self.conflict_service = ConflictDetectionService(self.generation_service.llm_provider)
        else:
            self.conflict_service = conflict_service

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

            config = get_config().retrieval
            history = ChatRepository.list_turns_by_session(session_id)

            # Retrieval
            retrieved_chunks, trace = self.advanced_retrieval_service.retrieve(
                query_text=query_text,
                config=config,
                collection_ids=[session.collection_id] if session.collection_id else [],
            )

            if is_cancelled(turn_id):
                yield self._format_sse("status", {"stage": "cancelled", "message": "Cancelled."})
                return

            # 3. Chunk safety check
            checked_chunks = self.safety_service.check_chunks(retrieved_chunks)
            safe_chunks = [c for c in checked_chunks if c.get("safety_risk") != "high"]

            if len(safe_chunks) < len(retrieved_chunks):
                logger.info(f"Filtered out {len(retrieved_chunks) - len(safe_chunks)} high-risk chunks in stream.")
            retrieved_chunks = safe_chunks

            # 4. Evaluate grounding
            is_sufficient, refusal_reason = self.grounding_service.evaluate_evidence(retrieved_chunks)

            # Update safety_trace with grounding info
            if not is_sufficient:
                safety_trace.answerability.is_answerable = False
                safety_trace.answerability.refusal_reason = refusal_reason
                safety_trace.groundedness.status = "unsupported"
            else:
                safety_trace.groundedness.status = "supported"
                # Real score computed later in finalize_turn; leave as None until then
                safety_trace.groundedness.score = None

            # Create turn record
            chunk_ids = [c["chunk_id"] for c in retrieved_chunks if c.get("chunk_id")]
            annotations = load_chunk_notes(chunk_ids)
            context_package = self.context_service.assemble_context(
                query_text=query_text,
                retrieved_chunks=retrieved_chunks,
                chat_history=history,
                collection_ids=[session.collection_id] if session.collection_id else [],
                annotations=annotations,
            )

            context_package["retrieval_trace"] = trace.model_dump() if hasattr(trace, 'model_dump') else (trace.dict() if hasattr(trace, 'dict') else trace)
            context_package["safety_trace"] = safety_trace.model_dump() if hasattr(safety_trace, 'model_dump') else (safety_trace.dict() if hasattr(safety_trace, 'dict') else safety_trace)

            ChatRepository.create_turn(
                id=turn_id,
                session_id=session_id,
                query_text=query_text,
                retrieved_chunks_json=json.dumps(_json_safe(retrieved_chunks)),
                context_used_json=json.dumps(_json_safe(context_package)),
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
            intent = trace.classification if trace else None
            for token in self.generation_service.generate_answer(context_package, stream=True, intent=intent):
                if is_cancelled(turn_id):
                    ChatRepository.update_turn_status(turn_id, "cancelled")
                    yield self._format_sse("status", {"stage": "cancelled", "message": "Cancelled."})
                    return
                token_str = str(token)
                full_answer += token_str
                yield self._format_sse("token", {"content": token_str})

            # 7. Status: Finalizing citations
            yield self._format_sse("status", {"stage": "finalizing", "message": "Finalizing citations..."})

            if is_cancelled(turn_id):
                ChatRepository.update_turn_status(turn_id, "cancelled")
                yield self._format_sse("status", {"stage": "cancelled", "message": "Cancelled."})
                return

            # Shared finalize: provenance + groundedness + citations + conflict
            finalize_result = finalize_turn(
                answer_text=full_answer,
                retrieved_chunks=retrieved_chunks,
                context_package=context_package,
                llm_provider=self.generation_service.llm_provider,
                grounding_service=self.grounding_service,
                chat_repository=ChatRepository,
                turn_id=turn_id,
                conflict_service=getattr(self, "conflict_service", None),
            )
            score = finalize_result["groundedness_score"]
            safety_trace.groundedness.score = score
            safety_trace.groundedness.status = "supported" if score >= 0.7 else "partial"

            # Include safety trace, retrieval trace, full chunks, and provenance
            yield self._format_sse("citations", {
                "citations": finalize_result["citations"],
                "retrieved_chunks": retrieved_chunks,
                "retrieval_trace": trace.model_dump() if hasattr(trace, 'model_dump') else (trace.dict() if hasattr(trace, 'dict') else trace),
                "safety_trace": safety_trace.model_dump() if hasattr(safety_trace, 'model_dump') else (safety_trace.dict() if hasattr(safety_trace, 'dict') else safety_trace),
                "conflict_status": finalize_result["conflict_status"],
                "conflict_details": finalize_result["conflict_details"],
                "groundedness_score": score,
                "provenance": finalize_result["provenance"],
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
        """Format data as an SSE event string, with numpy-to-native coercion."""
        return f"event: {event}\ndata: {json.dumps(_json_safe(data))}\n\n"


from fastapi import Depends
from chat.context import get_context_service
from chat.generation import get_generation_service
from chat.citations import get_citation_service
from chat.advanced_retrieval import get_advanced_retrieval_service

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
