import json

from flask import Blueprint, Response, current_app, jsonify, request, stream_with_context

from backend.services.answerability_service import AnswerabilityService
from backend.services.cancellation_manager import CancellationManager
from backend.services.chat_orchestration_service import ChatOrchestrationService
from backend.services.chat_service import ChatSessionService
from backend.services.context_packing_service import ContextPackingService
from backend.services.generation_service import ResponseGenerationService
from backend.services.run_record_service import RunRecordService
from backend.services.retrieval_service import RetrievalService
from backend.services.safety_decision_service import SafetyDecisionService
from backend.services.safety_scanner_service import SafetyScannerService


chat_blueprint = Blueprint("chat", __name__, url_prefix="/api/chat")


def _chat_service():
    return ChatSessionService(current_app.config["SQLITE_PATH"])


def _retrieval_service():
    return RetrievalService(
        sqlite_path=current_app.config["SQLITE_PATH"],
        chroma_client=current_app.extensions["chroma_client"],
        collection_prefix=current_app.config["CHROMA_COLLECTION_PREFIX"],
        embedding_model=current_app.config["DEFAULT_EMBEDDING_MODEL"],
        embedding_dimensions=current_app.config["EMBEDDING_DIMENSIONS"],
        top_k=current_app.config["CHAT_RETRIEVAL_TOP_K"],
        hybrid_semantic_weight=current_app.config["HYBRID_SEMANTIC_WEIGHT"],
        hybrid_keyword_weight=current_app.config["HYBRID_KEYWORD_WEIGHT"],
    )


def _orchestration_service():
    cancellation_manager = current_app.extensions.setdefault("cancellation_manager", CancellationManager())
    return ChatOrchestrationService(
        chat_service=_chat_service(),
        retrieval_service=_retrieval_service(),
        cancellation_manager=cancellation_manager,
        answerability_service=AnswerabilityService(
            min_similarity_threshold=current_app.config["ANSWERABILITY_MIN_SIMILARITY"],
            min_chunk_count=current_app.config["ANSWERABILITY_MIN_CHUNK_COUNT"],
            min_query_overlap=current_app.config["ANSWERABILITY_MIN_QUERY_OVERLAP"],
            consistency_threshold=current_app.config["ANSWERABILITY_CONSISTENCY_THRESHOLD"],
        ),
        context_packing_service=ContextPackingService(
            token_budget=current_app.config["CHAT_CONTEXT_TOKEN_BUDGET"]
        ),
        generation_service=ResponseGenerationService(
            provider_name=current_app.config["GENERATION_PROVIDER"],
            openai_api_key=current_app.config.get("OPENAI_API_KEY"),
            openai_model=current_app.config.get("OPENAI_MODEL", "gpt-5.5"),
            openai_base_url=current_app.config.get("OPENAI_BASE_URL"),
            openai_reasoning_effort=current_app.config.get("OPENAI_REASONING_EFFORT", "low"),
        ),
        safety_scanner_service=SafetyScannerService(
            rules=current_app.config["SAFETY_RULE_PATTERNS"],
        ),
        safety_decision_service=SafetyDecisionService(
            warn_threshold=current_app.config["SAFETY_WARN_RISK_THRESHOLD"],
            lower_trust_threshold=current_app.config["SAFETY_LOWER_TRUST_RISK_THRESHOLD"],
            exclude_threshold=current_app.config["SAFETY_EXCLUDE_RISK_THRESHOLD"],
            refuse_threshold=current_app.config["SAFETY_REFUSE_RISK_THRESHOLD"],
            multi_issue_refuse_total=current_app.config["SAFETY_MULTI_ISSUE_REFUSE_TOTAL"],
        ),
        run_record_service=RunRecordService(current_app.config["SQLITE_PATH"]),
        history_message_limit=current_app.config["CHAT_HISTORY_MAX_MESSAGES"],
    )


@chat_blueprint.post("/sessions")
def create_session():
    payload = request.get_json(silent=True) or {}
    session = _chat_service().create_session(
        collection_id=payload.get("collection_id"),
        retrieval_mode=(payload.get("retrieval_mode") or current_app.config["DEFAULT_CHAT_RETRIEVAL_MODE"]),
        user_id=payload.get("user_id"),
        metadata=payload.get("metadata"),
    )
    return jsonify(session), 201


@chat_blueprint.get("/sessions")
def list_sessions():
    return jsonify({"items": _chat_service().list_sessions()})


@chat_blueprint.get("/sessions/<session_id>")
def get_session(session_id):
    session = _chat_service().get_session(session_id)
    if not session:
        return jsonify({"error": "Chat session not found"}), 404
    return jsonify(session)


@chat_blueprint.post("/sessions/<session_id>/ask")
def ask_question(session_id):
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400
    result, error = _orchestration_service().orchestrate_turn(
        session_id=session_id,
        question_text=question,
        retrieval_mode_override=payload.get("retrieval_mode"),
        collection_override=payload.get("collection_id"),
        is_streaming=False,
    )
    if error:
        return jsonify({"error": error}), 404
    return jsonify(result)


@chat_blueprint.post("/sessions/<session_id>/ask-stream")
def ask_question_stream(session_id):
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400
    orchestration_service = _orchestration_service()

    @stream_with_context
    def generate():
        for event in orchestration_service.stream_turn(
            session_id=session_id,
            question_text=question,
            retrieval_mode_override=payload.get("retrieval_mode"),
            collection_override=payload.get("collection_id"),
        ):
            yield json.dumps(event) + "\n"

    return Response(generate(), mimetype="application/x-ndjson")


@chat_blueprint.post("/sessions/<session_id>/turns/<turn_id>/cancel")
def cancel_turn(session_id, turn_id):
    turn = _chat_service().get_turn(turn_id)
    if not turn or turn["session_id"] != session_id:
        return jsonify({"error": "Turn not found"}), 404
    current_app.extensions.setdefault("cancellation_manager", CancellationManager()).cancel_turn(turn_id)
    updated_turn = _chat_service().mark_turn_cancel_requested(turn_id)
    return jsonify({"status": "cancelled", "partial_state": updated_turn})


@chat_blueprint.get("/sessions/<session_id>/citations/<citation_id>")
def get_citation_detail(session_id, citation_id):
    citation = _chat_service().get_citation_detail(session_id, citation_id)
    if not citation:
        return jsonify({"error": "Citation not found"}), 404
    return jsonify(citation)


@chat_blueprint.get("/logs")
def list_chat_logs():
    return jsonify({"items": _chat_service().list_logs(session_id=request.args.get("session_id"))})
