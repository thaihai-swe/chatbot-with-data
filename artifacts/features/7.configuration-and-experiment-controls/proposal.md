# Proposal: Configuration and Experiment Controls (JSON)

## 💡 The Problem
The system currently lacks a centralized way to manage behavior across the RAG pipeline (ingestion, retrieval, generation). Settings are likely scattered or hard-coded, making experiments hard to reproduce and making it difficult for users to "tune" the system without deep code changes.

## 🎯 Objectives
- Centralize all behavior-shaping parameters into a single, editable JSON file.
- Ensure experiment reproducibility by saving the "effective" settings for every run into a dedicated artifact.
- Enable the UI to persist behavioral changes directly to the system's configuration.

## 🛠 High-Level Approach
1.  **Master Configuration:** A primary JSON file (e.g., `config/settings.json`) will serve as the source of truth for all behavioral settings.
2.  **Secret Separation:** Sensitive keys (OpenAI API key, database credentials) will remain in `.env`, while the JSON file handles logic parameters (chunk size, hybrid weights, etc.).
3.  **Run Artifacts:** For every significant operation (like an ingestion job or a chat session), the system will export a "snapshot" JSON file representing the exact configuration applied at that moment.
4.  **UI Integration:** The frontend will provide a settings panel. Changes made here will be sent to the backend and written back to the master JSON file to ensure they persist for future runs.

## ⚠️ Known Constraints / Risks
- **Concurrency:** Multiple users changing settings simultaneously could lead to race conditions when writing to the master JSON file.
- **Validation:** Manual edits to the JSON file could introduce syntax errors or out-of-bounds values (e.g., `temperature: 5.0`) that crash the system.

## ✅ Success Criteria
- [ ] A `settings.json` file exists and controls the core RAG pipeline behavior.
- [ ] Changing a value in the JSON file (or UI) immediately affects the next run without code changes.
- [ ] Every chat or ingestion run generates a timestamped "run config" JSON for audit/reproducibility.

---
**Status:** 🟢 Aligned
