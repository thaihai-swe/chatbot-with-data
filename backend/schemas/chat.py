from __future__ import annotations

from typing import Optional, List, Any, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    pass


class ChatSessionCreate(BaseModel):
    collection_ids: Optional[List[str]] = Field(default_factory=list, description="Collection IDs to scope the chat. Empty for all collections.")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict)


class ChatSessionResponse(BaseModel):
    id: str
    collection_ids: List[str] = Field(default_factory=list)
    metadata_json: str
    created_at: str
    updated_at: str


class AdvancedRetrievalConfig(BaseModel):
    retrieval_mode: Optional[str] = Field(None, description="Override global search mode (semantic, keyword, hybrid)")
    hybrid_weight: Optional[float] = Field(None, description="Override global hybrid weight (0.0 to 1.0)")
    enable_intelligence: bool = Field(True, description="Enable query classification and pre-retrieval intelligence")
    enable_rewriting: bool = Field(True, description="Enable query normalization (Rewriting)")
    enable_expansion: bool = Field(True, description="Enable LLM-based query expansion")
    expansion_count: int = Field(3, description="Number of expanded queries to generate")
    enable_decomposition: bool = Field(True, description="Enable decomposition of complex multi-hop queries")
    enable_hyde: bool = Field(True, description="Enable Hypothetical Document Embeddings (HyDE)")
    enable_synonym_expansion: bool = Field(True, description="Enable synonym mapping")
    enable_dynamic_routing: bool = Field(True, description="Enable dynamic routing based on query classification")
    enable_reranking: bool = Field(True, description="Enable post-retrieval reranking")
    reranker_model: Optional[str] = Field(None, description="Model to use for reranking")
    reranker_top_k: Optional[int] = Field(None, description="Final number of chunks to return after reranking")
    enable_parent_child: bool = Field(True, description="Enable parent-child chunk retrieval")
    enable_collection_routing: bool = Field(False, description="Enable automatic collection routing")
    collection_routing_threshold: float = Field(0.7, description="Confidence threshold for collection routing")
    collection_routing_max_collections: int = Field(3, description="Max collections to route to")
    enable_multi_hop: bool = Field(False, description="Enable multi-hop reasoning for complex queries")
    max_hops: int = Field(3, description="Maximum number of reasoning hops (1-5)")
    multi_hop_timeout_ms: int = Field(30000, description="Timeout for multi-hop queries in milliseconds")


class ChatTurnCreate(BaseModel):
    query_text: str = Field(..., min_length=1)
    advanced_config: Optional[AdvancedRetrievalConfig] = Field(default_factory=AdvancedRetrievalConfig)


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


ChatTurnResponse.model_rebuild()
