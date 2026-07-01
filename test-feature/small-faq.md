# Frequently Asked Questions

**Q: What is Retrieval-Augmented Generation (RAG)?**
A: RAG is a technique that combines information retrieval with text generation. When a user asks a question, the system first retrieves relevant chunks from a knowledge base, then provides those chunks as context to an LLM to generate a grounded answer with citations.

**Q: How does chunking affect RAG quality?**
A: Chunking determines how documents are split into retrievable pieces. Good chunking preserves semantic boundaries, maintains heading context, and produces coherent units. Poor chunking can fragment information and reduce retrieval precision.

**Q: What chunking strategies are available?**
A: The system supports adaptive tiering (full-doc injection for small documents), fixed-size, heading-aware, page-aware, semantic, and parent-child chunking.

**Q: How do I re-chunk an existing document?**
A: Open the document detail view and click the "Re-chunk" button. This re-runs the chunking pipeline with current settings and atomically replaces old chunks.

**Q: What is adaptive tiering?**
A: Adaptive tiering is a Notebook LM-inspired feature that injects small documents as single chunks (preserving full context) while routing larger documents to structural chunking strategies.
