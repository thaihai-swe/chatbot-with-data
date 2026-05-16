import logging
import json
import os
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import Depends

from chat.service import ChatService, get_chat_service
from chat.judge import JudgeService, get_judge_service
from schemas.evaluation import (
    EvaluationCase,
    EvaluationDataset,
    EvaluationResult,
    EvaluationRun,
    CaseMetrics
)
from schemas.chat import AdvancedRetrievalConfig
from repositories.chat_repository import ChatRepository

logger = logging.getLogger(__name__)

DATASETS_DIR = "backend/data/eval/datasets"
RUNS_DIR = "backend/data/eval/runs"


class EvaluationService:
    """Service for running batch evaluations on RAG performance."""

    def __init__(self, chat_service: ChatService, judge_service: JudgeService):
        self.chat_service = chat_service
        self.judge_service = judge_service
        os.makedirs(DATASETS_DIR, exist_ok=True)
        os.makedirs(RUNS_DIR, exist_ok=True)

    def list_datasets(self) -> List[EvaluationDataset]:
        """List all available evaluation datasets."""
        datasets = []
        for filename in os.listdir(DATASETS_DIR):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(DATASETS_DIR, filename), "r") as f:
                        data = json.load(f)
                        datasets.append(EvaluationDataset(**data))
                except Exception as e:
                    logger.error(f"Error loading dataset {filename}: {str(e)}")
        return datasets

    def get_dataset(self, dataset_id: str) -> Optional[EvaluationDataset]:
        """Get a specific dataset by ID."""
        path = os.path.join(DATASETS_DIR, f"{dataset_id}.json")
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            data = json.load(f)
            return EvaluationDataset(**data)

    def save_dataset(self, dataset: EvaluationDataset) -> None:
        """Save or update a dataset."""
        dataset.updated_at = datetime.utcnow().isoformat()
        if not dataset.created_at:
            dataset.created_at = dataset.updated_at
        
        path = os.path.join(DATASETS_DIR, f"{dataset.id}.json")
        with open(path, "w") as f:
            f.write(dataset.model_dump_json(indent=2))

    def run_evaluation(self, dataset_id: str, config: AdvancedRetrievalConfig) -> str:
        """
        Trigger an evaluation run. Returns the run_id.
        The actual execution should be handled via a background task in the router.
        """
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")

        run_id = f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        run = EvaluationRun(
            id=run_id,
            dataset_id=dataset_id,
            config=config.dict(),
            status="pending",
            created_at=datetime.utcnow().isoformat()
        )
        self._save_run(run)
        return run_id

    def execute_run(self, run_id: str) -> None:
        """Execute a pending evaluation run."""
        logger.info(f"Starting background execution for run {run_id}")
        run = self._get_run(run_id)
        if not run:
            logger.error(f"Run {run_id} not found for execution")
            return

        dataset = self.get_dataset(run.dataset_id)
        if not dataset:
            run.status = "failed"
            run.metrics_summary = {"error": "Dataset missing"}
            self._save_run(run)
            return

        run.status = "running"
        run.started_at = datetime.utcnow().isoformat()
        self._save_run(run)

        # Create a temporary session for the run
        session_id = f"eval_{run_id}"
        ChatRepository.create_session(id=session_id, metadata_json=json.dumps({"type": "evaluation", "run_id": run_id}))

        results = []
        try:
            for case in dataset.cases:
                result = self._evaluate_case(case, session_id, AdvancedRetrievalConfig(**run.config))
                results.append(result)
                # Save partial results periodically if needed
            
            run.results = results
            run.status = "completed"
            run.completed_at = datetime.utcnow().isoformat()
            run.metrics_summary = self._calculate_summary(results)
        except Exception as e:
            logger.error(f"Error during run {run_id}: {str(e)}")
            run.status = "failed"
            run.metrics_summary = {"error": str(e)}
        finally:
            self._save_run(run)

    def _evaluate_case(self, case: EvaluationCase, session_id: str, config: AdvancedRetrievalConfig) -> EvaluationResult:
        """Run a single evaluation case."""
        t0 = time.time()
        try:
            # Process the turn
            response = self.chat_service.process_turn(
                session_id=session_id,
                query_text=case.question,
                advanced_config=config
            )
            latency_ms = int((time.time() - t0) * 1000)

            # Retrieve chunks for hit/recall calculation
            retrieved_chunks = json.loads(response.retrieved_chunks_json)
            retrieved_ids = [c.get("document_id") for c in retrieved_chunks]
            
            hit = False
            recall = 0.0
            if case.expected_document_ids:
                intersection = set(retrieved_ids).intersection(set(case.expected_document_ids))
                hit = len(intersection) > 0
                recall = len(intersection) / len(case.expected_document_ids)

            # LLM-as-a-judge metrics
            groundedness = self.judge_service.evaluate_groundedness(response.answer_text, retrieved_chunks)
            relevance = self.judge_service.evaluate_relevance(case.question, response.answer_text)

            return EvaluationResult(
                case_id=case.id,
                actual_answer=response.answer_text,
                retrieved_chunk_ids=[c.get("id", c.get("chunk_id")) for c in retrieved_chunks],
                metrics=CaseMetrics(
                    groundedness=groundedness,
                    relevance=relevance,
                    hit=hit,
                    recall_at_k=recall,
                    latency_ms=latency_ms
                ),
                trace_id=response.id # The turn ID serves as the trace ID
            )
        except Exception as e:
            logger.error(f"Error evaluating case {case.id}: {str(e)}")
            return EvaluationResult(
                case_id=case.id,
                error=str(e)
            )

    def _calculate_summary(self, results: List[EvaluationResult]) -> Dict[str, float]:
        """Aggregate metrics across all results."""
        successful_results = [r for r in results if r.error is None]
        if not successful_results:
            return {}

        count = len(successful_results)
        return {
            "avg_groundedness": sum(r.metrics.groundedness.score for r in successful_results if r.metrics.groundedness) / count,
            "avg_relevance": sum(r.metrics.relevance.score for r in successful_results if r.metrics.relevance) / count,
            "avg_latency_ms": sum(r.metrics.latency_ms for r in successful_results) / count,
            "hit_rate": sum(1 for r in successful_results if r.metrics.hit) / count,
            "avg_recall": sum(r.metrics.recall_at_k for r in successful_results) / count,
            "total_cases": float(len(results)),
            "success_rate": count / len(results)
        }

    def _save_run(self, run: EvaluationRun) -> None:
        """Persist a run to JSON."""
        path = os.path.join(RUNS_DIR, f"{run.id}.json")
        with open(path, "w") as f:
            f.write(run.model_dump_json(indent=2))

    def _get_run(self, run_id: str) -> Optional[EvaluationRun]:
        """Load a run from JSON."""
        path = os.path.join(RUNS_DIR, f"{run_id}.json")
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            data = json.load(f)
            return EvaluationRun(**data)

    def list_runs(self) -> List[EvaluationRun]:
        """List all evaluation runs, sorted by timestamp desc."""
        runs = []
        for filename in os.listdir(RUNS_DIR):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(RUNS_DIR, filename), "r") as f:
                        data = json.load(f)
                        runs.append(EvaluationRun(**data))
                except Exception as e:
                    logger.error(f"Error loading run {filename}: {str(e)}")
        
        return sorted(runs, key=lambda x: x.id, reverse=True)


def get_evaluation_service(
    chat_service: ChatService = Depends(get_chat_service),
    judge_service: JudgeService = Depends(get_judge_service)
) -> EvaluationService:
    """Factory function for EvaluationService."""
    return EvaluationService(chat_service, judge_service)
