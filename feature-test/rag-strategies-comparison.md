# RAG Strategies: A Comparative Analysis

## Executive Summary

Retrieval-Augmented Generation (RAG) has become the dominant architecture for building production-grade question-answering systems over private knowledge bases. This document compares three primary RAG strategies — Naive RAG, Advanced RAG, and Modular RAG — across dimensions of complexity, retrieval quality, and generation fidelity.

## Naive RAG

Naive RAG follows the simplest possible pipeline: chunk documents, embed chunks into a vector database, retrieve the top-k most similar chunks for a user query, and feed them as context to a large language model. This approach was first popularized by the original 2020 Lewis et al. paper "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks."

The main advantage of Naive RAG is its simplicity. A basic implementation can be built in under 100 lines of Python using libraries like LangChain or LlamaIndex. However, Naive RAG suffers from three critical limitations. First, retrieval quality is highly sensitive to chunk size and embedding model choice; small chunks lose context while large chunks include noise. Second, there is no query reformulation — the raw user query is used for retrieval, which frequently fails for complex or multi-part questions. Third, Naive RAG has no mechanism for handling cases where the retrieved documents contradict each other, leading to hallucinations or inconsistent answers.

## Advanced RAG

Advanced RAG introduces pre-retrieval and post-retrieval techniques to address the shortcomings of the naive approach. Pre-retrieval methods include query rewriting, query expansion, and HyDE (Hypothetical Document Embeddings). Post-retrieval methods include re-ranking, context compression, and passage filtering.

The key innovation in Advanced RAG is the introduction of a re-ranking step. After retrieving the top-k chunks from the vector database, a cross-encoder model scores each chunk against the query. This significantly improves precision because cross-encoders capture deeper semantic relationships than bi-encoder embeddings used in the initial retrieval. Re-ranking typically adds 50-200ms of latency per query but improves top-3 accuracy by 15-25% in most benchmarks.

Another important technique in Advanced RAG is query rewriting. Instead of using the raw user query, a small LLM first reformulates the query into a more search-friendly form. For example, the query "Tell me about the limitations" might be rewritten as "What are the main limitations of Naive RAG?" This step alone can improve retrieval recall by 20-30%.

## Modular RAG

Modular RAG represents the most sophisticated approach, where the RAG pipeline is broken into independent modules that can be composed, reconfigured, and optimized separately. Common modules include a query router, a retrieval scheduler, a memory module for conversation history, and a verification module for fact-checking generated responses.

The modular architecture enables several advanced capabilities. A query router can direct different types of questions to different retrieval strategies — for example, factual queries might use sparse retrieval (BM25) while semantic queries use dense retrieval. A verification module can check each generated statement against the retrieved context, flagging unsupported claims. Modular RAG systems also support iterative retrieval, where the initial answer informs a second round of retrieval to fill knowledge gaps.

The main trade-off with Modular RAG is operational complexity. Each module introduces its own latency, failure modes, and maintenance burden. In production deployments at scale, the total system complexity can approach that of a full microservices architecture.

## Retrieval Quality Comparison

When comparing retrieval accuracy across these three approaches, the benchmarks show a clear progression. On the Natural Questions dataset, Naive RAG achieves a top-5 recall of approximately 62%, Advanced RAG reaches 78-82%, and Modular RAG can achieve 85-90% depending on module configuration. Precision follows a similar pattern: Naive RAG at 55%, Advanced RAG at 71%, and Modular RAG at 78%.

It is important to note that these numbers are highly dependent on the quality of the underlying embedding model and the specific domain. In specialized domains like legal or medical text, the gap between approaches narrows because the embedding models themselves become the bottleneck.

## When to Use Each Approach

Naive RAG is suitable for prototyping, internal tools with low accuracy requirements, or applications where latency must be under 500ms. Many production systems start with Naive RAG and progressively add advanced techniques as quality requirements increase.

Advanced RAG is the recommended starting point for any customer-facing production system. The addition of re-ranking and query rewriting provides substantial quality improvements with moderate engineering cost. Most commercial RAG products, including those from Glean and Notion AI, use Advanced RAG as their base architecture.

Modular RAG should be reserved for systems where retrieval quality is the primary differentiator and engineering resources are available. Examples include legal research platforms, scientific literature search, and enterprise knowledge management for large organizations.

## Conclusion

The choice of RAG strategy depends on the specific requirements of the application. Teams should start simple with Naive RAG, measure quality gaps, and incrementally adopt advanced techniques as needed. The most common mistake in RAG system design is over-engineering the retrieval pipeline while neglecting other critical aspects like chunking strategy, prompt design, and evaluation methodology.
