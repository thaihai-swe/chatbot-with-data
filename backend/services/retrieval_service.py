import math
import re

from backend.persistence.db import get_connection
from backend.services.indexing_service import IndexingService


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}


class RetrievalService:
    def __init__(
        self,
        sqlite_path,
        chroma_client,
        collection_prefix="collection",
        embedding_model="local-hash-v1",
        embedding_dimensions=32,
        top_k=5,
        hybrid_semantic_weight=0.6,
        hybrid_keyword_weight=0.4,
    ):
        self.sqlite_path = sqlite_path
        self.chroma_client = chroma_client
        self.collection_prefix = collection_prefix
        self.embedding_model = embedding_model
        self.embedding_dimensions = embedding_dimensions
        self.top_k = top_k
        self.hybrid_semantic_weight = hybrid_semantic_weight
        self.hybrid_keyword_weight = hybrid_keyword_weight
        self._indexing = IndexingService(
            chroma_client,
            collection_prefix=collection_prefix,
            embedding_model=embedding_model,
            dimensions=embedding_dimensions,
        )

    def _tokenize(self, text):
        return [token for token in re.findall(r"[a-z0-9]+", (text or "").lower()) if token not in STOPWORDS]

    def _list_collection_ids(self):
        with get_connection(self.sqlite_path) as connection:
            rows = connection.execute(
                "SELECT DISTINCT COALESCE(collection_id, '') AS collection_id FROM chunk_metadata"
            ).fetchall()
        return [row["collection_id"] or None for row in rows]

    def _chunk_rows_by_ids(self, chunk_ids):
        if not chunk_ids:
            return {}
        placeholders = ", ".join("?" for _ in chunk_ids)
        with get_connection(self.sqlite_path) as connection:
            rows = connection.execute(
                f"SELECT * FROM chunk_metadata WHERE chunk_id IN ({placeholders})",
                chunk_ids,
            ).fetchall()
        return {row["chunk_id"]: row for row in rows}

    def _page_or_section(self, chunk):
        if chunk.get("page_number"):
            return f"page {chunk['page_number']}"
        return chunk.get("section_name")

    def _serialize_chunk(self, chunk, retrieval_mode, score, keyword_hits=0, query_terms=None):
        query_terms = query_terms or []
        snippet = (chunk.get("chunk_text") or "").strip()
        return {
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["document_id"],
            "document_title": chunk.get("title"),
            "page_or_section": self._page_or_section(chunk),
            "source_url": chunk.get("source_url"),
            "content_snippet": snippet[:280],
            "full_text": snippet,
            "retrieval_score": score,
            "retrieval_mode": retrieval_mode,
            "collection_id": chunk.get("collection_id"),
            "chunk_order": chunk.get("chunk_order"),
            "page_number": chunk.get("page_number"),
            "section_name": chunk.get("section_name"),
            "source_type": chunk.get("source_type"),
            "keyword_hits": keyword_hits,
            "query_overlap": self._query_overlap(query_terms, snippet),
        }

    def _query_overlap(self, query_terms, text):
        if not query_terms:
            return 0.0
        text_tokens = set(self._tokenize(text))
        if not text_tokens:
            return 0.0
        overlap = len(set(query_terms) & text_tokens)
        return overlap / len(set(query_terms))

    def retrieve_semantic(self, question, collection_id=None):
        query_embedding = self._indexing._embed(question)
        query_terms = self._tokenize(question)
        collection_ids = [collection_id] if collection_id is not None else self._list_collection_ids()
        candidate_rows = []
        for candidate_collection_id in collection_ids:
            collection_name = self._indexing._collection_name(candidate_collection_id)
            try:
                collection = self.chroma_client.get_or_create_collection(name=collection_name)
            except Exception:
                continue
            result = collection.query(
                query_embeddings=[query_embedding],
                n_results=self.top_k,
                include=["metadatas", "documents", "distances"],
            )
            ids = (result.get("ids") or [[]])[0]
            metadatas = (result.get("metadatas") or [[]])[0]
            distances = (result.get("distances") or [[]])[0]
            chunk_rows = self._chunk_rows_by_ids(ids)
            for chunk_id, metadata, distance in zip(ids, metadatas, distances):
                chunk = chunk_rows.get(chunk_id)
                if not chunk:
                    continue
                vector_similarity = max(0.0, 1.0 - float(distance))
                overlap_similarity = self._query_overlap(query_terms, chunk.get("chunk_text"))
                similarity = max(vector_similarity, overlap_similarity)
                candidate_rows.append(
                    self._serialize_chunk(
                        chunk,
                        retrieval_mode="semantic",
                        score=round(similarity, 4),
                        query_terms=query_terms,
                    )
                )
        candidate_rows.sort(key=lambda item: item["retrieval_score"], reverse=True)
        return {
            "retrieved_chunks": candidate_rows[: self.top_k],
            "metadata": {
                "retrieval_mode_used": "semantic",
                "collection_filter_applied": collection_id,
                "rank_count": min(len(candidate_rows), self.top_k),
                "query_embedding": query_embedding,
            },
        }

    def retrieve_keyword(self, question, collection_id=None):
        query_terms = self._tokenize(question)
        if not query_terms:
            return {
                "retrieved_chunks": [],
                "metadata": {
                    "retrieval_mode_used": "keyword",
                    "collection_filter_applied": collection_id,
                    "rank_count": 0,
                },
            }
        sql = "SELECT * FROM chunk_metadata WHERE 1 = 1"
        params = []
        if collection_id is not None:
            sql += " AND collection_id = ?"
            params.append(collection_id)
        with get_connection(self.sqlite_path) as connection:
            rows = connection.execute(sql, params).fetchall()
        ranked = []
        for row in rows:
            haystack = f"{row.get('title') or ''} {row.get('chunk_text') or ''}".lower()
            keyword_hits = sum(haystack.count(term) for term in query_terms)
            if keyword_hits <= 0:
                continue
            score = round(self._query_overlap(query_terms, haystack), 4)
            ranked.append(self._serialize_chunk(row, "keyword", score, keyword_hits=keyword_hits, query_terms=query_terms))
        ranked.sort(key=lambda item: (item["keyword_hits"], item["retrieval_score"]), reverse=True)
        return {
            "retrieved_chunks": ranked[: self.top_k],
            "metadata": {
                "retrieval_mode_used": "keyword",
                "collection_filter_applied": collection_id,
                "rank_count": min(len(ranked), self.top_k),
            },
        }

    def retrieve_hybrid(self, question, collection_id=None):
        semantic = self.retrieve_semantic(question, collection_id=collection_id)
        keyword = self.retrieve_keyword(question, collection_id=collection_id)
        merged = {}
        for chunk in semantic["retrieved_chunks"]:
            merged[chunk["chunk_id"]] = {**chunk, "semantic_score": chunk["retrieval_score"], "keyword_score": 0.0}
        for chunk in keyword["retrieved_chunks"]:
            if chunk["chunk_id"] not in merged:
                merged[chunk["chunk_id"]] = {**chunk, "semantic_score": 0.0, "keyword_score": chunk["retrieval_score"]}
            else:
                merged[chunk["chunk_id"]]["keyword_score"] = chunk["retrieval_score"]
                merged[chunk["chunk_id"]]["keyword_hits"] = chunk.get("keyword_hits", 0)

        hybrid_rows = []
        for chunk in merged.values():
            combined = round(
                (chunk.get("semantic_score", 0.0) * self.hybrid_semantic_weight)
                + (chunk.get("keyword_score", 0.0) * self.hybrid_keyword_weight),
                4,
            )
            chunk["retrieval_score"] = combined
            chunk["retrieval_mode"] = "hybrid"
            hybrid_rows.append(chunk)
        hybrid_rows.sort(key=lambda item: item["retrieval_score"], reverse=True)
        return {
            "retrieved_chunks": hybrid_rows[: self.top_k],
            "metadata": {
                "retrieval_mode_used": "hybrid",
                "collection_filter_applied": collection_id,
                "rank_count": min(len(hybrid_rows), self.top_k),
            },
        }

    def retrieve(self, question, collection_id=None, retrieval_mode="semantic"):
        mode = (retrieval_mode or "semantic").lower()
        if mode == "keyword":
            return self.retrieve_keyword(question, collection_id=collection_id)
        if mode == "hybrid":
            return self.retrieve_hybrid(question, collection_id=collection_id)
        return self.retrieve_semantic(question, collection_id=collection_id)
