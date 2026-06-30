from typing import Any, Dict, List

from providers.base import BaseRerankingProvider


class DummyRerankingProvider(BaseRerankingProvider):
    """Dummy reranking provider that just sorts by the existing similarity score."""

    def __init__(self, model_name: str = "dummy-reranker"):
        self.model_name = model_name

    def rerank(self, query: str, chunks: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        """Sort chunks by their pre-existing 'similarity_score' in descending order."""
        if not chunks:
            return chunks

        sorted_chunks = sorted(
            chunks, key=lambda c: c.get("similarity_score", 0), reverse=True
        )[:top_k]
        
        return sorted_chunks

    def get_model_name(self) -> str:
        return self.model_name


class FlashRankProvider(BaseRerankingProvider):
    """Real cross-encoder reranking provider using flashrank."""

    def __init__(self, model_name: str = "ms-marco-MiniLM-L-12-v2"):
        import logging
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.logger.info(f"Loading FlashRank model: {self.model_name}")
        
        try:
            from flashrank import Ranker
            # Ranker caches the model weights in memory
            self.ranker = Ranker(model_name=self.model_name)
        except ImportError:
            self.logger.error("FlashRank is not installed. Run: pip install flashrank")
            raise

    def rerank(self, query: str, chunks: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        if not chunks:
            return chunks

        from flashrank import RerankRequest

        # FlashRank expects passages as a list of dicts with 'id' and 'text'
        passages = []
        for c in chunks:
            # Safely handle missing text
            text = c.get("text", "")
            if not text and c.get("page_content"):
                text = c.get("page_content")
            
            passages.append({
                "id": str(c.get("chunk_id", "")),
                "text": text,
                "original_chunk": c  # Keep a reference to the original dictionary
            })

        # Score the passages
        req = RerankRequest(query=query, passages=passages)
        results = self.ranker.rerank(req)
        
        # Results are already sorted by flashrank by default, but we'll map them back
        # to our expected schema, taking only the top_k.
        sorted_chunks = []
        for res in results[:top_k]:
            original_chunk = res.pop("original_chunk")
            # Flashrank injects 'score', we'll map it to 'rerank_score'
            original_chunk["rerank_score"] = res.get("score", 0)
            sorted_chunks.append(original_chunk)

        return sorted_chunks

    def get_model_name(self) -> str:
        return self.model_name
