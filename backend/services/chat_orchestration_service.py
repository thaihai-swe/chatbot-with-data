import time

from backend.services.answerability_service import AnswerabilityService
from backend.services.citation_service import CitationFormattingService
from backend.services.context_packing_service import ContextPackingService
from backend.services.generation_service import ResponseGenerationService
from backend.services.refusal_service import RefusalService
from backend.services.safety_decision_service import SafetyDecisionService
from backend.services.safety_scanner_service import SafetyScannerService


class ChatOrchestrationService:
    def __init__(
        self,
        chat_service,
        retrieval_service,
        cancellation_manager,
        answerability_service=None,
        context_packing_service=None,
        citation_service=None,
        generation_service=None,
        refusal_service=None,
        safety_scanner_service=None,
        safety_decision_service=None,
        run_record_service=None,
        history_message_limit=6,
    ):
        self.chat_service = chat_service
        self.retrieval_service = retrieval_service
        self.cancellation_manager = cancellation_manager
        self.answerability_service = answerability_service or AnswerabilityService()
        self.context_packing_service = context_packing_service or ContextPackingService()
        self.citation_service = citation_service or CitationFormattingService()
        self.generation_service = generation_service or ResponseGenerationService()
        self.refusal_service = refusal_service or RefusalService()
        self.safety_scanner_service = safety_scanner_service or SafetyScannerService()
        self.safety_decision_service = safety_decision_service or SafetyDecisionService()
        self.run_record_service = run_record_service
        self.history_message_limit = history_message_limit

    def _history_aware_question(self, question_text, conversation_history):
        history_lines = []
        for message in conversation_history or []:
            if message.get("role") != "user":
                continue
            content = (message.get("content") or "").strip()
            if not content:
                continue
            history_lines.append(content)
        if not history_lines:
            return question_text
        return "\n".join([*history_lines[-2:], question_text])

    def _groundedness_status(self, answerable, safety_result, result_type):
        if safety_result["overall_action"] == "refuse":
            return "refused_for_safety"
        if result_type == "refusal":
            return "unsupported"
        if safety_result["safety_issue_count"] > 0:
            return "grounded_with_warnings"
        return "grounded"

    def _answerability_flag(self, answerability_result, result_type):
        if result_type == "refusal":
            return bool(answerability_result.get("answerable"))
        return bool(answerability_result.get("answerable"))

    def _compose_response(
        self,
        *,
        result_type,
        answer,
        refusal,
        citations,
        retrieval_metadata,
        answerability_result,
        terminal_status,
        turn_id,
        session_id,
        turn,
        safety_result,
        run_id=None,
        excluded_chunks=None,
    ):
        groundedness_status = self._groundedness_status(answerability_result.get("answerable"), safety_result, result_type)
        return {
            "result_type": result_type,
            "answer": answer,
            "refusal": refusal,
            "citations": citations,
            "retrieval_metadata": retrieval_metadata,
            "answerability_score": answerability_result.get("answerability_score"),
            "terminal_status": terminal_status,
            "turn_id": turn_id,
            "session_id": session_id,
            "messages": self.chat_service.get_turn_messages(turn_id),
            "turn": turn,
            "run_id": run_id,
            "answerability_flag": self._answerability_flag(answerability_result, result_type),
            "groundedness_status": groundedness_status,
            "prompt_injection_result": safety_result["prompt_injection_result"],
            "prompt_injection_risk_score": safety_result["prompt_injection_risk_score"],
            "safety_issue_count": safety_result["safety_issue_count"],
            "warning_summary": safety_result.get("warning_summary"),
            "excluded_evidence_notice": safety_result.get("excluded_evidence_notice"),
            "refusal_reason": (refusal or {}).get("reason_category"),
            "safety_issues": safety_result.get("issues", []),
            "excluded_chunks": excluded_chunks or [],
        }

    def _persist_run_record(
        self,
        *,
        turn_id,
        session_id,
        question_text,
        answer_text,
        refusal_reason,
        answerability_result,
        safety_result,
        latency_ms,
        token_count,
        retrieval_mode,
        collection_id,
        result_type,
        retrieval_metadata,
        generation_metadata,
        all_retrieved_chunks,
        selected_context_chunks,
        excluded_chunks,
        citations,
        response_payload,
        conversation_history,
        rewritten_query=None,
    ):
        if not self.run_record_service:
            return None
        debug_snapshot = {
            "query_mode": "original",
            "rewritten_query": rewritten_query,
            "conversation_history": conversation_history,
            "retrieval_filters": {"collection_id": collection_id},
            "all_retrieved_chunks": all_retrieved_chunks,
            "selected_context_chunks": selected_context_chunks,
            "excluded_chunks_with_reasons": excluded_chunks,
            "citations": citations,
            "final_answer_or_refusal": {
                "result_type": result_type,
                "answer_text": answer_text if result_type == "answer" else None,
                "refusal_text": answer_text if result_type == "refusal" else None,
                "refusal_reason": refusal_reason,
            },
            "safety_decision": {
                "overall_action": safety_result["overall_action"],
                "prompt_injection_result": safety_result["prompt_injection_result"],
                "warning_summary": safety_result.get("warning_summary"),
                "excluded_evidence_notice": safety_result.get("excluded_evidence_notice"),
            },
            "response_payload": response_payload,
        }
        record = self.run_record_service.create_run_record(
            turn_id=turn_id,
            session_id=session_id,
            query_text=question_text,
            answer_text=answer_text,
            refusal_reason=refusal_reason,
            answerability_flag=bool(answerability_result.get("answerable")),
            answerability_score=answerability_result.get("answerability_score"),
            groundedness_status=response_payload["groundedness_status"],
            prompt_injection_result=safety_result["prompt_injection_result"],
            prompt_injection_risk_score=safety_result["prompt_injection_risk_score"],
            safety_issues=safety_result.get("issues", []),
            latency_ms=latency_ms,
            token_count=token_count,
            model_name=(generation_metadata or {}).get("model") or self.generation_service.provider_name,
            embedding_model=getattr(self.retrieval_service, "embedding_model", None),
            retrieval_mode_used=retrieval_mode,
            selected_collection_id=collection_id,
            result_type=result_type,
            warning_summary=safety_result.get("warning_summary"),
            excluded_evidence_notice=safety_result.get("excluded_evidence_notice"),
            retrieval_metadata=retrieval_metadata,
            generation_metadata=generation_metadata,
            answerability=answerability_result,
            debug_snapshot=debug_snapshot,
            observability_metadata={
                "retrieval_mode": retrieval_mode,
                "selected_collection_id": collection_id,
                "prompt_injection_result": safety_result["prompt_injection_result"],
            },
        )
        return record["run_id"]

    def _refusal_result(self, question_text, safety_reason=None):
        reason_category = safety_reason or "no_relevant_evidence"
        return {
            "answerable": False,
            "answerability_score": 0.0,
            "reason_category": reason_category,
            "supporting_metrics": {
                "top_similarity": 0.0,
                "chunk_count": 0,
                "query_overlap": 0.0,
                "consistency_score": 0.0,
            },
        }

    def _cancelled_result(self, turn_id, retrieval_metadata=None, supporting_metrics=None):
        turn = self.chat_service.mark_turn_cancelled(
            turn_id,
            retrieval_metadata=retrieval_metadata,
            supporting_metrics=supporting_metrics,
        )
        return {
            "result_type": "cancelled",
            "answer": None,
            "refusal": None,
            "citations": [],
            "retrieval_metadata": retrieval_metadata or {},
            "answerability_score": None,
            "terminal_status": "cancelled",
            "turn_id": turn_id,
            "session_id": turn["session_id"] if turn else None,
        }

    def orchestrate_turn(self, session_id, question_text, retrieval_mode_override=None, collection_override=None, is_streaming=False):
        started_at = time.perf_counter()
        session = self.chat_service.get_session(session_id)
        if not session:
            return None, "Chat session not found"
        conversation_history = self.chat_service.get_recent_session_history(
            session_id,
            limit=self.history_message_limit,
        )

        retrieval_mode = retrieval_mode_override or session["retrieval_mode"]
        collection_id = collection_override if collection_override is not None else session["collection_id"]
        turn = self.chat_service.create_turn(
            session_id=session_id,
            question_text=question_text,
            selected_collection_id=collection_id,
            retrieval_mode=retrieval_mode,
            is_streaming=is_streaming,
        )
        turn_id = turn["turn_id"]
        query_issues = self.safety_scanner_service.scan_user_query(question_text)
        retrieval_question = self._history_aware_question(question_text, conversation_history)

        retrieval_result = self.retrieval_service.retrieve(
            retrieval_question,
            collection_id=collection_id,
            retrieval_mode=retrieval_mode,
        )
        chunk_issues = self.safety_scanner_service.scan_retrieved_chunks(retrieval_result["retrieved_chunks"])
        safety_result = self.safety_decision_service.decide(query_issues + chunk_issues)
        filtered_chunks, excluded_chunks = self.safety_decision_service.apply_to_chunks(
            retrieval_result["retrieved_chunks"], safety_result
        )
        retrieval_result["metadata"]["safety"] = {
            "prompt_injection_result": safety_result["prompt_injection_result"],
            "prompt_injection_risk_score": safety_result["prompt_injection_risk_score"],
            "safety_issue_count": safety_result["safety_issue_count"],
        }
        if self.cancellation_manager.is_cancelled(turn_id):
            return self._cancelled_result(turn_id, retrieval_metadata=retrieval_result["metadata"]), None

        packed = self.context_packing_service.pack(filtered_chunks)
        answerability = self.answerability_service.evaluate(retrieval_question, filtered_chunks)

        if self.cancellation_manager.is_cancelled(turn_id):
            return self._cancelled_result(
                turn_id,
                retrieval_metadata=retrieval_result["metadata"],
                supporting_metrics=answerability["supporting_metrics"],
            ), None

        if safety_result["overall_action"] == "refuse":
            answerability = self._refusal_result(question_text, safety_reason="prompt_injection_risk")
            refusal = self.refusal_service.generate_refusal(answerability)
            completed_turn = self.chat_service.complete_turn(
                turn_id=turn_id,
                result_type="refusal",
                assistant_content=refusal["refusal_text"],
                terminal_status="refused",
                refusal_category=refusal["reason_category"],
                retrieval_mode_used=retrieval_mode,
                answerability_score=answerability["answerability_score"],
                retrieval_metadata=retrieval_result["metadata"],
                generation_metadata={},
                supporting_metrics=refusal["supporting_metrics"],
                packed_context=packed["selected_chunks"],
                citations=[],
            )
            self.chat_service.log_turn(
                turn_id=turn_id,
                session_id=session_id,
                question_text=question_text,
                retrieval_mode_used=retrieval_mode,
                retrieved_chunk_count=len(filtered_chunks),
                answerability_score=answerability["answerability_score"],
                refusal_category=refusal["reason_category"],
                answer_length_tokens=len(refusal["refusal_text"].split()),
                final_citation_count=0,
                metadata={"result_type": "refusal", "safety_result": safety_result},
            )
            payload = self._compose_response(
                result_type="refusal",
                answer=None,
                refusal=refusal,
                citations=[],
                retrieval_metadata=retrieval_result["metadata"],
                answerability_result=answerability,
                terminal_status="refused",
                turn_id=turn_id,
                session_id=session_id,
                turn=completed_turn,
                safety_result=safety_result,
                excluded_chunks=excluded_chunks,
            )
            payload["run_id"] = self._persist_run_record(
                turn_id=turn_id,
                session_id=session_id,
                question_text=question_text,
                answer_text=refusal["refusal_text"],
                refusal_reason=refusal["reason_category"],
                answerability_result=answerability,
                safety_result=safety_result,
                latency_ms=int((time.perf_counter() - started_at) * 1000),
                token_count=len(refusal["refusal_text"].split()),
                retrieval_mode=retrieval_mode,
                collection_id=collection_id,
                result_type="refusal",
                retrieval_metadata=retrieval_result["metadata"],
                generation_metadata={},
                all_retrieved_chunks=retrieval_result["retrieved_chunks"],
                selected_context_chunks=packed["selected_chunks"],
                excluded_chunks=excluded_chunks,
                citations=[],
                response_payload=payload,
                conversation_history=conversation_history,
                rewritten_query=retrieval_question if retrieval_question != question_text else None,
            )
            return payload, None

        if not answerability["answerable"]:
            refusal = self.refusal_service.generate_refusal(answerability)
            completed_turn = self.chat_service.complete_turn(
                turn_id=turn_id,
                result_type="refusal",
                assistant_content=refusal["refusal_text"],
                terminal_status="refused",
                refusal_category=refusal["reason_category"],
                retrieval_mode_used=retrieval_mode,
                answerability_score=answerability["answerability_score"],
                retrieval_metadata=retrieval_result["metadata"],
                generation_metadata={},
                supporting_metrics=refusal["supporting_metrics"],
                packed_context=packed["selected_chunks"],
                citations=[],
            )
            self.chat_service.log_turn(
                turn_id=turn_id,
                session_id=session_id,
                question_text=question_text,
                retrieval_mode_used=retrieval_mode,
                retrieved_chunk_count=len(filtered_chunks),
                answerability_score=answerability["answerability_score"],
                refusal_category=refusal["reason_category"],
                answer_length_tokens=len(refusal["refusal_text"].split()),
                final_citation_count=0,
                metadata={"result_type": "refusal", "safety_result": safety_result},
            )
            payload = self._compose_response(
                result_type="refusal",
                answer=None,
                refusal=refusal,
                citations=[],
                retrieval_metadata=retrieval_result["metadata"],
                answerability_result=answerability,
                terminal_status="refused",
                turn_id=turn_id,
                session_id=session_id,
                turn=completed_turn,
                safety_result=safety_result,
                excluded_chunks=excluded_chunks,
            )
            payload["run_id"] = self._persist_run_record(
                turn_id=turn_id,
                session_id=session_id,
                question_text=question_text,
                answer_text=refusal["refusal_text"],
                refusal_reason=refusal["reason_category"],
                answerability_result=answerability,
                safety_result=safety_result,
                latency_ms=int((time.perf_counter() - started_at) * 1000),
                token_count=len(refusal["refusal_text"].split()),
                retrieval_mode=retrieval_mode,
                collection_id=collection_id,
                result_type="refusal",
                retrieval_metadata=retrieval_result["metadata"],
                generation_metadata={},
                all_retrieved_chunks=retrieval_result["retrieved_chunks"],
                selected_context_chunks=packed["selected_chunks"],
                excluded_chunks=excluded_chunks,
                citations=[],
                response_payload=payload,
                conversation_history=conversation_history,
                rewritten_query=retrieval_question if retrieval_question != question_text else None,
            )
            return payload, None

        generated = self.generation_service.generate(
            question_text,
            packed["selected_chunks"],
            conversation_history=conversation_history,
        )
        if self.cancellation_manager.is_cancelled(turn_id):
            return self._cancelled_result(
                turn_id,
                retrieval_metadata=retrieval_result["metadata"],
                supporting_metrics=answerability["supporting_metrics"],
            ), None

        citations = self.citation_service.format_citations(
            packed["selected_chunks"],
            citation_indices=generated.get("citation_indices"),
            retrieval_mode=retrieval_mode,
        )
        completed_turn = self.chat_service.complete_turn(
            turn_id=turn_id,
            result_type="answer",
            assistant_content=generated["answer_text"],
            terminal_status="completed",
            retrieval_mode_used=retrieval_mode,
            answerability_score=answerability["answerability_score"],
            retrieval_metadata=retrieval_result["metadata"],
            generation_metadata=generated["generation_metadata"],
            supporting_metrics=answerability["supporting_metrics"],
            packed_context=packed["selected_chunks"],
            citations=citations,
        )
        self.chat_service.log_turn(
            turn_id=turn_id,
            session_id=session_id,
            question_text=question_text,
            retrieval_mode_used=retrieval_mode,
            retrieved_chunk_count=len(filtered_chunks),
            answerability_score=answerability["answerability_score"],
            refusal_category=None,
            answer_length_tokens=len(generated["answer_text"].split()),
            final_citation_count=len(citations),
            metadata={"result_type": "answer", "safety_result": safety_result},
        )
        payload = self._compose_response(
            result_type="answer",
            answer={
                "text": generated["answer_text"],
                "generation_metadata": generated["generation_metadata"],
            },
            refusal=None,
            citations=citations,
            retrieval_metadata=retrieval_result["metadata"],
            answerability_result=answerability,
            terminal_status="completed",
            turn_id=turn_id,
            session_id=session_id,
            turn=completed_turn,
            safety_result=safety_result,
            excluded_chunks=excluded_chunks,
        )
        payload["run_id"] = self._persist_run_record(
            turn_id=turn_id,
            session_id=session_id,
            question_text=question_text,
            answer_text=generated["answer_text"],
            refusal_reason=None,
            answerability_result=answerability,
            safety_result=safety_result,
            latency_ms=int((time.perf_counter() - started_at) * 1000),
            token_count=generated["generation_metadata"].get("tokens_used", len(generated["answer_text"].split())),
            retrieval_mode=retrieval_mode,
            collection_id=collection_id,
            result_type="answer",
            retrieval_metadata=retrieval_result["metadata"],
            generation_metadata=generated["generation_metadata"],
            all_retrieved_chunks=retrieval_result["retrieved_chunks"],
            selected_context_chunks=packed["selected_chunks"],
            excluded_chunks=excluded_chunks,
            citations=citations,
            response_payload=payload,
            conversation_history=conversation_history,
            rewritten_query=retrieval_question if retrieval_question != question_text else None,
        )
        return payload, None

    def stream_turn(self, session_id, question_text, retrieval_mode_override=None, collection_override=None):
        started_at = time.perf_counter()
        session = self.chat_service.get_session(session_id)
        if not session:
            yield {"event": "error", "error": "Chat session not found"}
            return
        conversation_history = self.chat_service.get_recent_session_history(
            session_id,
            limit=self.history_message_limit,
        )

        retrieval_mode = retrieval_mode_override or session["retrieval_mode"]
        collection_id = collection_override if collection_override is not None else session["collection_id"]
        turn = self.chat_service.create_turn(
            session_id=session_id,
            question_text=question_text,
            selected_collection_id=collection_id,
            retrieval_mode=retrieval_mode,
            is_streaming=True,
        )
        turn_id = turn["turn_id"]
        yield {"event": "turn_created", "turn_id": turn_id}
        yield {"event": "retrieving", "turn_id": turn_id}
        query_issues = self.safety_scanner_service.scan_user_query(question_text)
        retrieval_question = self._history_aware_question(question_text, conversation_history)

        retrieval_result = self.retrieval_service.retrieve(
            retrieval_question,
            collection_id=collection_id,
            retrieval_mode=retrieval_mode,
        )
        chunk_issues = self.safety_scanner_service.scan_retrieved_chunks(retrieval_result["retrieved_chunks"])
        safety_result = self.safety_decision_service.decide(query_issues + chunk_issues)
        filtered_chunks, excluded_chunks = self.safety_decision_service.apply_to_chunks(
            retrieval_result["retrieved_chunks"], safety_result
        )
        retrieval_result["metadata"]["safety"] = {
            "prompt_injection_result": safety_result["prompt_injection_result"],
            "prompt_injection_risk_score": safety_result["prompt_injection_risk_score"],
            "safety_issue_count": safety_result["safety_issue_count"],
        }
        yield {
            "event": "safety_checked",
            "turn_id": turn_id,
            "prompt_injection_result": safety_result["prompt_injection_result"],
            "prompt_injection_risk_score": safety_result["prompt_injection_risk_score"],
            "safety_issue_count": safety_result["safety_issue_count"],
            "warning_summary": safety_result.get("warning_summary"),
        }
        if self.cancellation_manager.is_cancelled(turn_id):
            self._cancelled_result(turn_id, retrieval_metadata=retrieval_result["metadata"])
            yield {"event": "cancelled", "turn_id": turn_id}
            return

        packed = self.context_packing_service.pack(filtered_chunks)
        yield {
            "event": "context_packed",
            "turn_id": turn_id,
            "chunk_count": len(packed["selected_chunks"]),
            "total_tokens": packed["total_tokens"],
        }
        answerability = self.answerability_service.evaluate(retrieval_question, filtered_chunks)
        yield {
            "event": "answerability_checked",
            "turn_id": turn_id,
            "answerability_score": answerability["answerability_score"],
            "reason_category": answerability["reason_category"],
        }

        if safety_result["overall_action"] == "refuse":
            answerability = self._refusal_result(question_text, safety_reason="prompt_injection_risk")
            refusal = self.refusal_service.generate_refusal(answerability)
            completed_turn = self.chat_service.complete_turn(
                turn_id=turn_id,
                result_type="refusal",
                assistant_content=refusal["refusal_text"],
                terminal_status="refused",
                refusal_category=refusal["reason_category"],
                retrieval_mode_used=retrieval_mode,
                answerability_score=answerability["answerability_score"],
                retrieval_metadata=retrieval_result["metadata"],
                generation_metadata={},
                supporting_metrics=refusal["supporting_metrics"],
                packed_context=packed["selected_chunks"],
                citations=[],
            )
            self.chat_service.log_turn(
                turn_id=turn_id,
                session_id=session_id,
                question_text=question_text,
                retrieval_mode_used=retrieval_mode,
                retrieved_chunk_count=len(filtered_chunks),
                answerability_score=answerability["answerability_score"],
                refusal_category=refusal["reason_category"],
                answer_length_tokens=len(refusal["refusal_text"].split()),
                final_citation_count=0,
                metadata={"result_type": "refusal", "streamed": True, "safety_result": safety_result},
            )
            payload = self._compose_response(
                result_type="refusal",
                answer=None,
                refusal=refusal,
                citations=[],
                retrieval_metadata=retrieval_result["metadata"],
                answerability_result=answerability,
                terminal_status="refused",
                turn_id=turn_id,
                session_id=session_id,
                turn=completed_turn,
                safety_result=safety_result,
                excluded_chunks=excluded_chunks,
            )
            payload["run_id"] = self._persist_run_record(
                turn_id=turn_id,
                session_id=session_id,
                question_text=question_text,
                answer_text=refusal["refusal_text"],
                refusal_reason=refusal["reason_category"],
                answerability_result=answerability,
                safety_result=safety_result,
                latency_ms=int((time.perf_counter() - started_at) * 1000),
                token_count=len(refusal["refusal_text"].split()),
                retrieval_mode=retrieval_mode,
                collection_id=collection_id,
                result_type="refusal",
                retrieval_metadata=retrieval_result["metadata"],
                generation_metadata={},
                all_retrieved_chunks=retrieval_result["retrieved_chunks"],
                selected_context_chunks=packed["selected_chunks"],
                excluded_chunks=excluded_chunks,
                citations=[],
                response_payload=payload,
                conversation_history=conversation_history,
                rewritten_query=retrieval_question if retrieval_question != question_text else None,
            )
            yield {"event": "completed", **payload}
            return

        if not answerability["answerable"]:
            refusal = self.refusal_service.generate_refusal(answerability)
            completed_turn = self.chat_service.complete_turn(
                turn_id=turn_id,
                result_type="refusal",
                assistant_content=refusal["refusal_text"],
                terminal_status="refused",
                refusal_category=refusal["reason_category"],
                retrieval_mode_used=retrieval_mode,
                answerability_score=answerability["answerability_score"],
                retrieval_metadata=retrieval_result["metadata"],
                generation_metadata={},
                supporting_metrics=refusal["supporting_metrics"],
                packed_context=packed["selected_chunks"],
                citations=[],
            )
            self.chat_service.log_turn(
                turn_id=turn_id,
                session_id=session_id,
                question_text=question_text,
                retrieval_mode_used=retrieval_mode,
                retrieved_chunk_count=len(filtered_chunks),
                answerability_score=answerability["answerability_score"],
                refusal_category=refusal["reason_category"],
                answer_length_tokens=len(refusal["refusal_text"].split()),
                final_citation_count=0,
                metadata={"result_type": "refusal", "streamed": True, "safety_result": safety_result},
            )
            payload = self._compose_response(
                result_type="refusal",
                answer=None,
                refusal=refusal,
                citations=[],
                retrieval_metadata=retrieval_result["metadata"],
                answerability_result=answerability,
                terminal_status="refused",
                turn_id=turn_id,
                session_id=session_id,
                turn=completed_turn,
                safety_result=safety_result,
                excluded_chunks=excluded_chunks,
            )
            payload["run_id"] = self._persist_run_record(
                turn_id=turn_id,
                session_id=session_id,
                question_text=question_text,
                answer_text=refusal["refusal_text"],
                refusal_reason=refusal["reason_category"],
                answerability_result=answerability,
                safety_result=safety_result,
                latency_ms=int((time.perf_counter() - started_at) * 1000),
                token_count=len(refusal["refusal_text"].split()),
                retrieval_mode=retrieval_mode,
                collection_id=collection_id,
                result_type="refusal",
                retrieval_metadata=retrieval_result["metadata"],
                generation_metadata={},
                all_retrieved_chunks=retrieval_result["retrieved_chunks"],
                selected_context_chunks=packed["selected_chunks"],
                excluded_chunks=excluded_chunks,
                citations=[],
                response_payload=payload,
                conversation_history=conversation_history,
                rewritten_query=retrieval_question if retrieval_question != question_text else None,
            )
            yield {"event": "completed", **payload}
            return

        generated = self.generation_service.generate(
            question_text,
            packed["selected_chunks"],
            conversation_history=conversation_history,
        )
        yield {"event": "generating", "turn_id": turn_id}
        for answer_chunk in self.generation_service.stream_answer_chunks(generated["answer_text"]):
            if self.cancellation_manager.is_cancelled(turn_id):
                self._cancelled_result(
                    turn_id,
                    retrieval_metadata=retrieval_result["metadata"],
                    supporting_metrics=answerability["supporting_metrics"],
                )
                yield {"event": "cancelled", "turn_id": turn_id}
                return
            yield {"event": "answer_chunk", "turn_id": turn_id, "text": answer_chunk}

        citations = self.citation_service.format_citations(
            packed["selected_chunks"],
            citation_indices=generated.get("citation_indices"),
            retrieval_mode=retrieval_mode,
        )
        self.chat_service.complete_turn(
            turn_id=turn_id,
            result_type="answer",
            assistant_content=generated["answer_text"],
            terminal_status="completed",
            retrieval_mode_used=retrieval_mode,
            answerability_score=answerability["answerability_score"],
            retrieval_metadata=retrieval_result["metadata"],
            generation_metadata=generated["generation_metadata"],
            supporting_metrics=answerability["supporting_metrics"],
            packed_context=packed["selected_chunks"],
            citations=citations,
        )
        self.chat_service.log_turn(
            turn_id=turn_id,
            session_id=session_id,
            question_text=question_text,
            retrieval_mode_used=retrieval_mode,
            retrieved_chunk_count=len(filtered_chunks),
            answerability_score=answerability["answerability_score"],
            refusal_category=None,
            answer_length_tokens=len(generated["answer_text"].split()),
            final_citation_count=len(citations),
            metadata={"result_type": "answer", "streamed": True, "safety_result": safety_result},
        )
        payload = self._compose_response(
            result_type="answer",
            answer={
                "text": generated["answer_text"],
                "generation_metadata": generated["generation_metadata"],
            },
            refusal=None,
            citations=citations,
            retrieval_metadata=retrieval_result["metadata"],
            answerability_result=answerability,
            terminal_status="completed",
            turn_id=turn_id,
            session_id=session_id,
            turn=self.chat_service.get_turn(turn_id),
            safety_result=safety_result,
            excluded_chunks=excluded_chunks,
        )
        payload["run_id"] = self._persist_run_record(
            turn_id=turn_id,
            session_id=session_id,
            question_text=question_text,
            answer_text=generated["answer_text"],
            refusal_reason=None,
            answerability_result=answerability,
            safety_result=safety_result,
            latency_ms=int((time.perf_counter() - started_at) * 1000),
            token_count=generated["generation_metadata"].get("tokens_used", len(generated["answer_text"].split())),
            retrieval_mode=retrieval_mode,
            collection_id=collection_id,
            result_type="answer",
            retrieval_metadata=retrieval_result["metadata"],
            generation_metadata=generated["generation_metadata"],
            all_retrieved_chunks=retrieval_result["retrieved_chunks"],
            selected_context_chunks=packed["selected_chunks"],
            excluded_chunks=excluded_chunks,
            citations=citations,
            response_payload=payload,
            conversation_history=conversation_history,
            rewritten_query=retrieval_question if retrieval_question != question_text else None,
        )
        yield {"event": "completed", **payload}
