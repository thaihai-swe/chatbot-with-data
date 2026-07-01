# Technical Reference Manual — Data Processing Pipeline

## Introduction

The data processing pipeline ingests raw documents, extracts structured information, and indexes it for fast retrieval. This manual covers the architecture, configuration, and operational procedures for each stage of the pipeline.

The pipeline consists of four main stages: ingestion, extraction, chunking, and indexing. Each stage is independently configurable and can be monitored via the admin dashboard.

## Ingestion Stage

### File Upload

Files are uploaded via the frontend UI or the REST API. Supported formats include PDF, Markdown, and plain text. The system validates file type, size (default max 50 MB), and performs a virus scan before accepting the upload.

### URL Ingestion

The system can also ingest content from URLs. It fetches the HTML, extracts the main content using readability algorithms, and processes it identically to uploaded files. URL ingestion supports authentication cookies for behind-paywall sources.

### Duplicate Detection

Before processing, the system checks for duplicates using three strategies: file hash (SHA256), normalized text hash, and similarity-based detection. When a duplicate is found, the system awaits user decision: skip, replace, create variant, or merge metadata.

## Extraction Stage

### PDF Extraction

PDF extraction uses PyMuPDF to extract text, page numbers, and structural elements. The system inserts page break markers (`###PAGE_BREAK###`) to enable page-aware chunking. Tables are extracted and flattened to text with row-column markers preserved.

### Markdown Extraction

Markdown files are parsed with a custom parser that preserves heading hierarchy, code blocks, lists, and inline formatting. Heading levels are tracked to enable heading-aware chunking with path preservation.

### Web Extraction

Web content uses a headless browser (Playwright) for JavaScript-rendered pages, followed by readability-cli for main content extraction. The system extracts metadata including author, publish date, and Open Graph tags.

## Chunking Stage

### Adaptive Tiering

The first decision in the chunking stage is whether the document qualifies for full-doc injection. Small documents below the configurable threshold are stored as single chunks with `adaptive_tier="full_doc"`. This preserves full context for small documents.

### Heading-Aware Chunking

For structured documents, the heading-aware strategy recursively extracts heading paths. Each chunk's text is prepended with its full heading lineage, ensuring that retrieved chunks always carry their section context.

### Semantic Chunking

The semantic strategy analyzes content similarity between adjacent sentences to find natural topic boundaries. When an embedding provider is available, it uses cosine similarity of real sentence embeddings. If the provider is unavailable or exceeds a 5-second timeout, it gracefully falls back to Jaccard similarity.

### Parent-Child Chunking

The parent-child strategy creates hierarchical chunk relationships. Children are small chunks optimized for search precision. Parents group children at heading boundaries (when headings are detected) or by fixed count (for unstructured text). When a child chunk matches a query, the system can optionally retrieve the full parent context for richer LLM input.

## Indexing Stage

### Embedding Generation

Each chunk is embedded using the configured embedding model (default: `text-embedding-3-small`). Embeddings are cached in SQLite to avoid recomputation. The system supports multiple embedding models and can re-embed chunks when the model changes.

### Vector Indexing

Chunks and their embeddings are indexed in Weaviate, which provides hybrid search (BM25 + semantic vector search). Each index entry tracks its source chunk, embedding, and generation number for lifecycle management.

### Safety Filtering

Before indexing, chunks pass through a three-layer safety filter: heuristic pattern matching, fuzzy similarity against known injection corpus, and LLM-based adversarial detection. High-risk chunks are blocked and logged.

## Configuration

### Settings File

All pipeline settings are stored in `config/settings.json` and can be modified via the Settings UI or direct file edit. Settings are applied immediately at runtime without server restart.

### Key Parameters

- `chunk_size`: Target token count per chunk (default: 1000)
- `chunk_overlap`: Token overlap between consecutive chunks (default: 200)
- `adaptive_tiering_enabled`: Toggle full-doc injection (default: true)
- `adaptive_tiering_ratio`: Fraction of context window for threshold (default: 0.3)
- `embedding_model`: Model for vector embeddings (default: text-embedding-3-small)
- `retrieval_mode`: Search mode: hybrid, semantic, or keyword (default: hybrid)

## Operations

### Monitoring

The admin dashboard shows real-time pipeline metrics: ingestion rate, chunk count, indexing latency, and error rates. Each pipeline stage logs to structured JSON for integration with log aggregation tools.

### Troubleshooting

Common issues include: file size exceeds limit, unsupported file type, extraction timeout for very large PDFs, embedding provider rate limiting, and Weaviate connectivity problems. Each issue produces a specific error code and remediation guidance in the logs.

### Re-chunking

Documents can be re-chunked on demand via the Re-chunk button in the document detail view. The operation is atomic: old chunks are saved before deletion and restored if the re-chunk fails. This allows users to apply new chunking strategies to previously ingested documents without data loss.
