from __future__ import annotations

from typing import Optional, List, Any
from pydantic import BaseModel, Field


class ChatSessionCreate(BaseModel):
    collection_id: Optional[str] = Field(None, description="Collection ID to scope the chat. None for all collections.")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict)


class ChatSessionResponse(BaseModel):
    id: str
    collection_id: Optional[str]
    metadata_json: str
    created_at: str
    updated_at: str


class AdvancedRetrievalConfig(BaseModel):
    enable_intelligence: bool = Field(False, description="Enable query classification and pre-retrieval intelligence")
    enable_expansion: bool = Field(False, description="Enable LLM-based query expansion")
    expansion_count: int = Field(3, description="Number of expanded queries to generate")
    enable_decomposition: bool = Field(False, description="Enable decomposition of complex multi-hop queries")
    enable_hyde: bool = Field(False, description="Enable Hypothetical Document Embeddings (HyDE)")
    enable_synonym_expansion: bool = Field(False, description="Enable synonym mapping")
    enable_dynamic_routing: bool = Field(False, description="Enable dynamic routing based on query classification")
    enable_reranking: bool = Field(False, description="Enable post-retrieval reranking")
    reranker_model: Optional[str] = Field(None, description="Model to use for reranking")
    reranker_top_k: Optional[int] = Field(None, description="Final number of chunks to return after reranking")
    enable_parent_child: bool = Field(False, description="Enable parent-child chunk retrieval")
    auto_collection_detection: bool = Field(False, description="Enable automatic detection of target collections")


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
    inferred_collections: List[str] = Field(default_factory=list)
    collection_confidence: Optional[float] = None


class RetrievalRunTrace(BaseModel):
    query: str
    raw_count: int
    top_scores: List[float] = Field(default_factory=list)


class RerankingTrace(BaseModel):
    model: str
    pre_order_ids: List[str] = Field(default_factory=list)
    post_order_ids: List[str] = Field(default_factory=list)
    latency_ms: Optional[int] = None


class RetrievalTrace(BaseModel):
    original_query: str
    classification: Optional[str] = None
    transformations: RetrievalTransformations = Field(default_factory=RetrievalTransformations)
    routing: RetrievalRouting = Field(default_factory=RetrievalRouting)
    retrieval_runs: List[RetrievalRunTrace] = Field(default_factory=list)
    merged_candidates_count: int = 0
    reranking: Optional[RerankingTrace] = None
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
