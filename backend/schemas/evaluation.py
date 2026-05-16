from __future__ import annotations

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class EvaluationCase(BaseModel):
    id: str = Field(..., description="Unique ID for the evaluation case")
    question: str = Field(..., description="The user question to evaluate")
    expected_answer: Optional[str] = Field(None, description="The ground truth answer (optional)")
    expected_document_ids: List[str] = Field(default_factory=list, description="IDs of documents that should be retrieved")
    tags: List[str] = Field(default_factory=list, description="Categorization tags (e.g., 'fact-lookup', 'multi-hop')")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context or parameters")


class EvaluationDataset(BaseModel):
    id: str = Field(..., description="Unique ID for the dataset")
    name: str = Field(..., description="Display name for the dataset")
    description: Optional[str] = None
    cases: List[EvaluationCase] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class JudgeMetric(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0, description="Score between 0 and 1")
    reason: str = Field(..., description="Explanation for the score")


class CaseMetrics(BaseModel):
    groundedness: Optional[JudgeMetric] = None
    relevance: Optional[JudgeMetric] = None
    hit: bool = Field(False, description="True if expected documents were retrieved")
    recall_at_k: float = 0.0
    latency_ms: int = 0


class EvaluationResult(BaseModel):
    case_id: str
    actual_answer: Optional[str] = None
    retrieved_chunk_ids: List[str] = Field(default_factory=list)
    metrics: CaseMetrics = Field(default_factory=CaseMetrics)
    trace_id: Optional[str] = None
    error: Optional[str] = None


class EvaluationRun(BaseModel):
    id: str = Field(..., description="Unique ID for the run (e.g., run_20260516_120000)")
    dataset_id: str
    config: Dict[str, Any] = Field(default_factory=dict, description="RAG configuration used for this run")
    status: str = "pending"  # pending, running, completed, failed
    metrics_summary: Dict[str, float] = Field(default_factory=dict)
    results: List[EvaluationResult] = Field(default_factory=list)
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
