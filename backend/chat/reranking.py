from __future__ import annotations

import time
from typing import Any, Dict, List, Tuple

from schemas.chat import RerankingTrace


class RerankingService:
    """Service for re-scoring candidates after retrieval."""

    def __init__(self, model: str = "dummy-reranker"):
        self.model = model

    def rerank(
        self, query_text: str, chunks: List[Dict[str, Any]], top_k: int
    ) -> Tuple[List[Dict[str, Any]], RerankingTrace]:
        if not chunks:
            return chunks, RerankingTrace(model=self.model)

        t0 = time.time()
        pre_order_ids = [str(c.get("chunk_id")) for c in chunks]

        sorted_chunks = sorted(
            chunks, key=lambda c: c.get("similarity_score", 0), reverse=True
        )[:top_k]

        post_order_ids = [str(c.get("chunk_id")) for c in sorted_chunks]

        trace = RerankingTrace(
            model=self.model,
            pre_order_ids=pre_order_ids,
            post_order_ids=post_order_ids,
            latency_ms=int((time.time() - t0) * 1000),
        )
        return sorted_chunks, trace


def get_reranking_service() -> RerankingService:
    return RerankingService()
