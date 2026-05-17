"""Service for running RAG evaluations and sanity checks."""
from __future__ import annotations

import logging
import json
import time
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import Depends
from chat.service import ChatService, get_chat_service
from schemas.chat import EvalResult, SanityCheckResponse, AdvancedRetrievalConfig, ChatTurnCreate
from config import get_settings

logger = logging.getLogger(__name__)


class EvaluationService:
    """Service for executing evaluation datasets and calculating metrics."""

    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service

    def _load_dataset(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load eval dataset: {str(e)}")
            return []

    async def run_sanity_check(self, dataset_path: str = "backend/data/eval_dataset.json") -> SanityCheckResponse:
        """
        Run the 10-20 'golden' test cases.
        """
        dataset = self._load_dataset(dataset_path)
        if not dataset:
            return SanityCheckResponse(
                timestamp=datetime.now().isoformat(),
                total_cases=0,
                passed_cases=0,
                overall_recall=0.0,
                overall_groundedness=0.0,
                results=[]
            )

        # We'll use a dummy session or create one for evaluation
        # For simplicity, we'll process each turn in isolation
        session_id = "eval-session"
        
        tasks = []
        for case in dataset:
            tasks.append(self._evaluate_case(case))
        
        results = await asyncio.gather(*tasks)

        total = len(results)
        passed = sum(1 for r in results if r.passed)
        avg_recall = sum(1 for r in results if r.recall_status) / total if total > 0 else 0.0
        avg_groundedness = sum(r.groundedness_score for r in results) / total if total > 0 else 0.0

        return SanityCheckResponse(
            timestamp=datetime.now().isoformat(),
            total_cases=total,
            passed_cases=passed,
            overall_recall=avg_recall,
            overall_groundedness=avg_groundedness,
            results=results
        )

    async def _evaluate_case(self, case: Dict[str, Any]) -> EvalResult:
        t0 = time.time()
        case_id = case.get("id", "unknown")
        question = case.get("question", "")
        expected_doc_id = case.get("expected_document_id", "")

        try:
            # We run with intelligence enabled by default for eval
            # Run in a thread if process_turn is blocking (it is)
            # In a real production app, we'd make ChatService async
            loop = asyncio.get_event_loop()
            
            # Note: We need a session. Let's assume 'default' exists or we mock it.
            # For the Lab, we'll just try to use a session 'eval'
            try:
                from repositories.chat_repository import ChatRepository
                if not ChatRepository.get_session("eval"):
                    ChatRepository.create_session("eval", [])
            except:
                pass

            response = await loop.run_in_executor(
                None, 
                self.chat_service.process_turn, 
                "eval", 
                question, 
                AdvancedRetrievalConfig()
            )

            # 1. Recall Check
            retrieved_chunks = json.loads(response.retrieved_chunks_json)
            retrieved_doc_ids = [str(c.get("document_id")) for c in retrieved_chunks]
            recall_status = expected_doc_id in retrieved_doc_ids

            # 2. Groundedness (already computed by ChatService now?)
            # Actually, I haven't updated ChatService yet.
            # Let's call calculate_groundedness directly here to be sure.
            score, reason = self.chat_service.grounding_service.calculate_groundedness(
                response.answer_text, 
                retrieved_chunks
            )

            latency = int((time.time() - t0) * 1000)
            
            # Pass criteria: Recall is True AND Groundedness > 0.7
            passed = recall_status and score >= 0.7

            return EvalResult(
                case_id=case_id,
                question=question,
                expected_document_id=expected_doc_id,
                actual_answer=response.answer_text,
                recall_status=recall_status,
                groundedness_score=score,
                groundedness_reason=reason,
                latency_ms=latency,
                passed=passed
            )

        except Exception as e:
            logger.error(f"Error evaluating case {case_id}: {str(e)}")
            return EvalResult(
                case_id=case_id,
                question=question,
                expected_document_id=expected_doc_id,
                actual_answer=f"ERROR: {str(e)}",
                passed=False
            )


def get_evaluation_service(chat_service: ChatService = Depends(get_chat_service)) -> EvaluationService:
    return EvaluationService(chat_service)
