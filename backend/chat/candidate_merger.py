from __future__ import annotations

from typing import Any, Dict, List


class CandidateMerger:
    """Service for merging candidate chunks from multiple retrieval runs using Reciprocal Rank Fusion."""

    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k

    def merge(
        self, results_list: List[List[Dict[str, Any]]], top_k: int = 10
    ) -> List[Dict[str, Any]]:
        if not results_list:
            return []

        chunk_map = {}
        rrf_scores = {}

        for results in results_list:
            for rank, chunk in enumerate(results):
                chunk_id = chunk.get("chunk_id")
                if not chunk_id:
                    continue
                if chunk_id not in chunk_map:
                    chunk_map[chunk_id] = chunk
                    rrf_scores[chunk_id] = 0.0
                rrf_scores[chunk_id] += 1.0 / (self.rrf_k + rank + 1)

        sorted_chunk_ids = sorted(
            rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True
        )

        merged_chunks = []
        for cid in sorted_chunk_ids[:top_k]:
            chunk = chunk_map[cid].copy()
            chunk["similarity_score"] = rrf_scores[cid]
            chunk["original_score"] = chunk_map[cid].get("original_score")
            merged_chunks.append(chunk)

        return merged_chunks
