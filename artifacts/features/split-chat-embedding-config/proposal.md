# Proposal: Split Chat and Embedding Configuration

## 💡 The Problem
Currently, chat and embedding services share the same API base URL (`OPENAI_API_BASE`) and key (`OPENAI_API_KEY`). This limits flexibility, particularly when using different providers or endpoints for embeddings versus chat models (e.g., chat via a cloud provider, embeddings via a local service).

## 🎯 Objectives
1. Decouple configuration for chat and embedding endpoints.
2. Enable independent API base URLs and API keys for each.
3. Maintain provider compatibility (OpenAI/Ollama/etc.) for both services.

## 🛠 High-Level Approach
1. Introduce new environment variables: `EMBEDDING_API_BASE` and `EMBEDDING_API_KEY`.
2. Update configuration loading logic (likely in `backend/config.py`) to parse these new variables.
3. Update relevant services (e.g., in `backend/chunking/` or `backend/embeddings/`) to use these dedicated configuration values when initializing clients.
4. Ensure backward compatibility: default to the singular `OPENAI_API_BASE`/`OPENAI_API_KEY` if the new ones are not provided.

## ⚠️ Known Constraints / Risks
- Need to ensure we don't break existing setups where users rely on shared configuration.
- Multiple services might need updates to fetch the correct configuration; need to identify all call sites.

## ✅ Success Criteria
- [ ] Ability to configure different API Base URLs for chat and embedding in `.env`.
- [ ] Ability to configure different API Keys for chat and embedding in `.env`.
- [ ] Verification that chat functionality remains unaffected by embedding configuration changes.
- [ ] Verification that embedding functionality works with the newly introduced variables.

---
**Status:** 🟢 Aligned
