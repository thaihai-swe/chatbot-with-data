from __future__ import annotations

import uuid
import json
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional

from repositories.chat_repository import ChatRepository
from schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatTurnCreate,
    ChatTurnResponse,
    CitationResponse,
    ProvenanceResponse,
    SanityCheckResponse,
    EvaluationRunResponse,
)
from chat.service import get_chat_service, ChatService
from chat.evaluation import get_evaluation_service, EvaluationService
from chat.streaming import get_streaming_orchestrator, StreamingOrchestrator
from chat.cancellation import cancel_turn

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/evaluate/sanity-check", response_model=SanityCheckResponse)
async def run_sanity_check(
    evaluation_service: EvaluationService = Depends(get_evaluation_service),
) -> SanityCheckResponse:
    """Run the 10-20 golden test cases evaluation."""
    return await evaluation_service.run_sanity_check()


@router.get("/evaluate/history", response_model=List[EvaluationRunResponse])
def get_evaluation_history() -> List[EvaluationRunResponse]:
    """Retrieve the 10 most recent evaluation runs."""
    from repositories.evaluation_repository import EvaluationRepository
    runs = EvaluationRepository.list_recent_runs(limit=10)
    return [EvaluationRunResponse(**r) for r in runs]


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(payload: ChatSessionCreate) -> ChatSessionResponse:
    """Create a new chat session."""
    session_id = str(uuid.uuid4())
    metadata_json = json.dumps(payload.metadata or {})
    
    collection_id = payload.collection_id if payload.collection_id else None

    session = ChatRepository.create_session(
        id=session_id,
        collection_id=collection_id,
        metadata_json=metadata_json,
    )

    return ChatSessionResponse(
        id=session.id,
        collection_id=session.collection_id,
        metadata_json=session.metadata_json,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.get("/sessions", response_model=List[ChatSessionResponse])
def list_sessions(collection_id: Optional[str] = None) -> List[ChatSessionResponse]:
    """List chat sessions, optionally filtered by collection ID."""
    sessions = ChatRepository.list_sessions(collection_id=collection_id)
    return [
        ChatSessionResponse(
            id=s.id,
            collection_id=s.collection_id,
            metadata_json=s.metadata_json,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_session(session_id: str) -> ChatSessionResponse:
    """Get a chat session by ID."""
    session = ChatRepository.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return ChatSessionResponse(
        id=session.id,
        collection_id=session.collection_id,
        metadata_json=session.metadata_json,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str) -> None:
    """Delete a chat session."""
    deleted = ChatRepository.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return


@router.get("/sessions/{session_id}/history", response_model=List[ChatTurnResponse])
def get_session_history(session_id: str) -> List[ChatTurnResponse]:
    """Get the history of turns for a session."""
    session = ChatRepository.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    turns = ChatRepository.list_turns_by_session(session_id)
    result = []

    for turn in turns:
        citations = ChatRepository.list_citations_by_turn(turn.id)
        citation_responses = [
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
        ]

        context_data = {}
        try:
            if turn.context_used_json:
                context_data = json.loads(turn.context_used_json)
        except Exception:
            pass

        result.append(
            ChatTurnResponse(
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
                citations=citation_responses,
                retrieval_trace=context_data.get("retrieval_trace"),
                safety_trace=context_data.get("safety_trace"),
                conflict_status=context_data.get("conflict_status", "no_conflict"),
                conflict_details=context_data.get("conflict_details"),
                provenance=json.loads(turn.provenance_json) if turn.provenance_json else None,
                provenance_json=turn.provenance_json,
            )
        )

    return result


@router.post("/sessions/{session_id}/turns", response_model=ChatTurnResponse, status_code=status.HTTP_201_CREATED)
def submit_turn(
    session_id: str,
    payload: ChatTurnCreate,
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatTurnResponse:
    """Submit a new chat turn (query)."""
    try:
        return chat_service.process_turn(
            session_id,
            payload.query_text
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/turns/stream")
async def submit_turn_stream(
    session_id: str,
    payload: ChatTurnCreate,
    orchestrator: StreamingOrchestrator = Depends(get_streaming_orchestrator),
) -> StreamingResponse:
    """Submit a new chat turn (query) and stream the response."""
    return StreamingResponse(
        orchestrator.stream_turn(
            session_id,
            payload.query_text
        ),
        media_type="text/event-stream",
    )


@router.post("/turns/{turn_id}/cancel")
def cancel_chat_turn(turn_id: str) -> dict:
    """Cancel an ongoing chat turn."""
    cancel_turn(turn_id)
    return {"status": "cancellation_requested", "turn_id": turn_id}


@router.get("/turns/{turn_id}/provenance", response_model=ProvenanceResponse)
def get_turn_provenance(turn_id: str) -> ProvenanceResponse:
    """Return claim-level provenance graph for a completed turn."""
    turn = ChatRepository.get_turn(turn_id)
    if not turn:
        raise HTTPException(status_code=404, detail="Turn not found")
    try:
        data = json.loads(turn.provenance_json or "{}")
    except Exception:
        data = {}
    if not data:
        return ProvenanceResponse()
    return ProvenanceResponse(**data)
