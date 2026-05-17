from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
import os

class IngestionSettings(BaseModel):
    allowed_file_types: List[str] = Field(default=["pdf", "txt", "md"])
    max_file_size_mb: int = Field(default=50, ge=1)
    url_ingestion_enabled: bool = True
    reingest_behavior: str = Field(default="skip")  # skip, overwrite
    duplicate_handling: str = Field(default="detect") # detect, allow
    duplicate_detection_enabled: bool = True
    duplicate_detection_method: str = Field(default="content_hash")
    near_duplicate_threshold: float = Field(default=0.95, ge=0.0, le=1.0)
    
    # Chunking
    chunk_size: int = Field(default=1000, ge=1)
    chunk_overlap: int = Field(default=200, ge=0)
    chunking_strategy: str = Field(default="fixed") # fixed, semantic, recursive
    semantic_chunking_enabled: bool = False
    semantic_similarity_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    parent_child_enabled: bool = False
    
    # Embedding & Vector DB (Infrastructure usually in .env, but some here for experiment)
    embedding_model: str = Field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
    embedding_batch_size: int = Field(default=100, ge=1)
    vector_db_collection: str = "DocumentChunk"

class RetrievalSettings(BaseModel):
    retrieval_mode: str = Field(default="hybrid") # semantic, keyword, hybrid
    top_k: int = Field(default=5, ge=1)
    hybrid_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    query_expansion_enabled: bool = False
    query_expansion_count: int = Field(default=3, ge=1, le=5)
    query_decomposition_enabled: bool = False
    hyde_enabled: bool = False
    synonym_expansion_enabled: bool = False
    dynamic_routing_enabled: bool = False
    reranker_enabled: bool = False
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranker_top_n: int = Field(default=3, ge=1)

class LLMSettings(BaseModel):
    provider: str = "openai"
    model: str = Field(default_factory=lambda: os.getenv("CHAT_MODEL", "gpt-4o"))
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1)
    system_prompt_template: Optional[str] = None
    chat_history_limit: int = Field(default=10, ge=0)
    streaming_enabled: bool = True

class SafetySettings(BaseModel):
    groundedness_check_enabled: bool = True
    prompt_injection_detection_enabled: bool = True
    injection_risk_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    refusal_threshold: float = Field(default=0.5, ge=0.0, le=1.0)

class EvaluationSettings(BaseModel):
    enabled_metrics: List[str] = Field(default=["faithfulness", "answer_relevance"])
    latency_tracking_enabled: bool = True
    token_usage_tracking_enabled: bool = True

class GlobalSettings(BaseModel):
    ingestion: IngestionSettings = Field(default_factory=IngestionSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    safety: SafetySettings = Field(default_factory=SafetySettings)
    evaluation: EvaluationSettings = Field(default_factory=EvaluationSettings)
