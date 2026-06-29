from __future__ import annotations

from typing import Optional, List, Any, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    pass


class ChatSessionCreate(BaseModel):
    collection_id: Optional[str] = Field(None, description="Collection ID to scope the chat. None for global/all collections.")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict)


class ChatSessionResponse(BaseModel):
    id: str
    collection_id: Optional[str] = None
    metadata_json: str
    created_at: str
    updated_at: str


class ChatTurnCreate(BaseModel):
    query_text: str = Field(..., min_length=1)


class CitationResponse(BaseModel):
    id: str
    turn_id: str
    chunk_id: str
    document_id: str
    quote_text: Optional[str]
    metadata_json: str
    created_at: str


class RetrievalTransformations(BaseModel):
    rewritten_query: Optional[str] = None
    expanded_queries: List[str] = Field(default_factory=list)
    sub_questions: List[str] = Field(default_factory=list)
    hyde_doc: Optional[str] = None
    synonym_expansions: dict[str, str] = Field(default_factory=dict)


class RetrievalRouting(BaseModel):
    selected_strategy: str = "baseline"
    reason: Optional[str] = None
    fallback_triggered: bool = False


class RetrievalRunTrace(BaseModel):
    query: str
    raw_count: int
    top_scores: List[float] = Field(default_factory=list)


class RerankingTrace(BaseModel):
    model: str
    pre_order_ids: List[str] = Field(default_factory=list)
    post_order_ids: List[str] = Field(default_factory=list)
    latency_ms: Optional[int] = None


class CollectionRoutingTrace(BaseModel):
    routing_decision: List[str] = Field(default_factory=list, description="Collection IDs selected by routing")
    confidence: Optional[float] = Field(None, description="Confidence score for routing decision (0.0-1.0)")
    reasoning: Optional[str] = Field(None, description="LLM reasoning for collection selection")
    fallback_reason: Optional[str] = Field(None, description="Reason for fallback to all collections")
    latency_ms: Optional[int] = Field(None, description="Latency of routing decision in milliseconds")


class ReasoningStep(BaseModel):
    hop_number: int = Field(..., description="Sequential hop number (1-indexed)")
    sub_question: str = Field(..., description="Sub-question for this hop")
    retrieved_chunk_ids: List[str] = Field(default_factory=list, description="Chunk IDs retrieved for this hop")
    intermediate_answer: Optional[str] = Field(None, description="Generated intermediate answer for this hop")
    latency_ms: Optional[int] = Field(None, description="Latency for this hop in milliseconds")
    failure: Optional[str] = Field(None, description="Failure reason if hop failed")


class ReasoningChainTrace(BaseModel):
    hops: List[ReasoningStep] = Field(default_factory=list, description="List of reasoning hops")
    total_hops: int = Field(0, description="Total number of hops executed")
    fallback_triggered: bool = Field(False, description="Whether fallback to original query was triggered")
    fallback_reason: Optional[str] = Field(None, description="Reason for fallback if triggered")
    total_latency_ms: Optional[int] = Field(None, description="Total latency for multi-hop reasoning in milliseconds")


class RetrievalTrace(BaseModel):
    original_query: str
    classification: Optional[str] = None
    classification_confidence: Optional[float] = None
    transformations: RetrievalTransformations = Field(default_factory=RetrievalTransformations)
    routing: RetrievalRouting = Field(default_factory=RetrievalRouting)
    retrieval_runs: List[RetrievalRunTrace] = Field(default_factory=list)
    merged_candidates_count: int = 0
    reranking: Optional[RerankingTrace] = None
    collection_routing: Optional[CollectionRoutingTrace] = None
    reasoning_chain: Optional[ReasoningChainTrace] = None
    parent_child_expansions_count: int = 0
    execution_time_ms: dict[str, int] = Field(default_factory=dict)


class SafetyGroundedness(BaseModel):
    score: Optional[float] = None
    status: str = "unchecked"


class SafetyAnswerability(BaseModel):
    is_answerable: bool = True
    refusal_reason: Optional[str] = None


class SafetyTrace(BaseModel):
    query_classification: Optional[str] = None
    injection_risk: str = "low"
    matched_patterns: List[str] = Field(default_factory=list)
    classifier_reason: Optional[str] = None
    groundedness: SafetyGroundedness = Field(default_factory=SafetyGroundedness)
    answerability: SafetyAnswerability = Field(default_factory=SafetyAnswerability)


class EvalResult(BaseModel):
    case_id: str
    question: str
    expected_document_id: str
    actual_answer: Optional[str] = None
    recall_status: bool = False
    groundedness_score: float = 0.0
    groundedness_reason: Optional[str] = None
    latency_ms: int = 0
    passed: bool = False


class SanityCheckResponse(BaseModel):
    timestamp: str
    total_cases: int
    passed_cases: int
    overall_recall: float
    overall_groundedness: float
    results: List[EvalResult] = Field(default_factory=list)


class ChatTurnResponse(BaseModel):
    id: str
    session_id: str
    query_text: str
    answer_text: Optional[str]
    retrieved_chunks_json: str
    context_used_json: str
    status: str
    safety_status: Optional[str] = None
    safety_risk_score: Optional[float] = None
    safety_reason: Optional[str] = None
    groundedness_score: Optional[float] = None
    error_message: Optional[str]
    created_at: str
    updated_at: str
    citations: List[CitationResponse] = []
    retrieval_trace: Optional[RetrievalTrace] = None
    safety_trace: Optional[SafetyTrace] = None
    conflict_status: Optional[str] = "no_conflict"
    conflict_details: Optional[str] = None


ChatTurnResponse.model_rebuild()
