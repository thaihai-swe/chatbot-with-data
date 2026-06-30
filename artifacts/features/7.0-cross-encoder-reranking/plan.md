# Implementation Plan: 7.0-cross-encoder-reranking

## Part 1: Technical Design

### 1. Architecture Map
- **Abstraction Layer:** Add `BaseRerankingProvider` to `backend/providers/base.py`.
- **Implementations:** 
  - `DummyRerankingProvider` (in `backend/providers/reranker.py`) implements simple sorting.
  - `FlashRankProvider` (in `backend/providers/reranker.py`) integrates the `flashrank` library.
- **Factory:** Update `backend/providers/factory.py` with a `get_reranker()` method that returns the configured provider.
- **Service Injection:** Modify `backend/chat/reranking.py` (`RerankingService`) to use the provider from `get_reranker()`.
- **Configuration:** Add `reranker_provider` (default `"dummy"`) and `flashrank_model` (default `"ms-marco-MiniLM-L-6-v2"`) to `backend/config.py`. Add `flashrank` to `requirements.txt`.

### 2. State & Data Models
- No changes to persistent databases or migrations.
- Data structures passed to the provider will be `List[Dict[str, Any]]` directly from the retrieval layer.
- `RerankingTrace` schema remains the same, ensuring it logs the `model` used by the active provider.

### 3. Component Design
- **`BaseRerankingProvider` (ABC in `providers/base.py`):**
  - `rerank(self, query: str, chunks: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]`
  - `get_model_name(self) -> str`
- **`DummyRerankingProvider` (in `providers/reranker.py`):**
  - Sorts chunks by existing `"similarity_score"` in descending order.
  - Returns `model_name = "dummy-reranker"`.
- **`FlashRankProvider` (in `providers/reranker.py`):**
  - `__init__(self, model_name: str)`: Instantiates `Ranker(model_name)` from `flashrank`. Maintains it as an instance variable.
  - `rerank`:
    - Converts input chunks to the list of dictionaries expected by FlashRank (containing `"id"` and `"text"`).
    - Calls `ranker.rerank(RerankRequest(query=query, passages=passages))`.
    - Merges the newly calculated scores (usually stored as `"score"` in FlashRank's output) back into the original chunk dictionaries as `"rerank_score"`.
    - Returns the top K sorted chunks.
- **`RerankingService` (in `chat/reranking.py`):**
  - `__init__(self, provider: BaseRerankingProvider)`
  - Delegates the sorting logic directly to `self.provider.rerank(...)`.
  - Constructs the `RerankingTrace` using `self.provider.get_model_name()`.

### 4. Risk Mitigation
- **Latency & Cold Start:** FlashRank models are tiny (~30MB for MiniLM), but downloading on the first request is slow. The `Ranker` instance should be cached. 
- **Missing Dependencies:** In CI/CD, if `flashrank` is not installed, it shouldn't break the dummy provider. We will handle imports carefully.
- **Ponytail Rule (Simplicity):** We avoid full generic plugin architectures. The factory just maps `"dummy" -> DummyRerankingProvider` and `"flashrank" -> FlashRankProvider`. 

---

## Part 2: Delivery Strategy

### 5. Task Breakdown
(See `tasks.md` for explicit task definitions.)

### 6. Verification Plan
- **Unit Tests (`backend/tests/chat/test_reranking.py`):**
  - Test `DummyRerankingProvider` sorts correctly.
  - Test `FlashRankProvider` initializes and scores text correctly.
  - Test `RerankingService` integration and `RerankingTrace` generation.
- **System Check:** Verify the dummy fallback runs quickly and that FlashRank significantly alters chunk ordering compared to base vector similarity.
