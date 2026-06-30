from __future__ import annotations

import time
from typing import Any, Dict, List, Tuple

from schemas.chat import RerankingTrace
from providers.base import BaseRerankingProvider
from providers.factory import get_reranker_provider


class RerankingService:
    """Service for re-scoring candidates after retrieval."""

    def __init__(self, provider: BaseRerankingProvider):
        self.provider = provider
        self.model = self.provider.get_model_name()

    def rerank(
        self, query_text: str, chunks: List[Dict[str, Any]], top_k: int
    ) -> Tuple[List[Dict[str, Any]], RerankingTrace]:
        if not chunks:
            return chunks, RerankingTrace(model=self.model)

        t0 = time.time()
        pre_order_ids = [str(c.get("chunk_id")) for c in chunks]

        # Delegate to the injected provider
        sorted_chunks = self.provider.rerank(query_text, chunks, top_k)

        post_order_ids = [str(c.get("chunk_id")) for c in sorted_chunks]

        trace = RerankingTrace(
            model=self.model,
            pre_order_ids=pre_order_ids,
            post_order_ids=post_order_ids,
            latency_ms=int((time.time() - t0) * 1000),
        )
        return sorted_chunks, trace


def get_reranking_service() -> RerankingService:
    return RerankingService(provider=get_reranker_provider())
