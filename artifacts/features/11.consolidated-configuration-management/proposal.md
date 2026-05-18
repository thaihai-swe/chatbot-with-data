# Proposal: Consolidated Configuration Management

## Problem
The current configuration management is split between a legacy `Settings` class (env-driven) and a modern `GlobalSettings` class (JSON-driven). Additionally, the recently implemented "Split Chat and Embedding" logic relies solely on environment variables. This creates a fragmented developer experience where some feature tweaks (like timeouts) require environment changes while others use JSON.

## Proposed Solution
Unify the configuration management system by clearly separating **Infrastructure** and **Feature** settings. Feature 11 will consolidate all experiment-worthy and feature-specific settings into the structured `GlobalSettings` system, while ensuring that core infrastructure credentials remain securely in the environment.

### Key Principles
1.  **Infrastructure (via .env):** API keys, Base URLs, and database paths remain strictly in environment variables. They are **not** user-changeable via the settings JSON/API for security and stability.
2.  **Features (via JSON):** Timeouts, similarity thresholds, context window sizes, and chunking parameters are moved to `GlobalSettings`. They are validated, persisted in `settings.json`, and changeable via the API.
3.  **Unified Access:** Services will consume settings from a consolidated source, with `GlobalSettings` using environment variables as their default values.

### Key Changes
- **Schema Updates:** Add `url_timeout_seconds`, `context_window_size`, `min_similarity_threshold`, and `min_results_count` to `GlobalSettings`.
- **Refactoring:** Update `UrlIngestionService`, `GroundingService`, and `LLMClient` to use the unified `get_config()` accessor for feature settings.
- **Legacy Cleanup:** Reduce reliance on the legacy `Settings` class for feature-level logic.

## Outcome
- A clean, professional configuration boundary: `.env` for infrastructure, `settings.json` for behavior.
- Enhanced flexibility for evaluations and experiments without server restarts.
- Consistent validation and persistence for all feature-level settings.

## Next Steps
- [ ] User alignment on this final unified proposal.
- [ ] Author detailed `spec.md`.
