# Proposal: Consolidate Settings Between .env and Setting UI

## 💡 The Problem
Currently, our settings are fragmented and conflated. The `.env` file mixes immutable infrastructure settings (like API keys) with mutable user preferences (like retrieval limits). The frontend Settings UI overwrites these user preferences in a separate JSON file, shadowing the `.env` values. Additionally, the Chat UI maintains separate, advanced toggles that do not sync with the global Settings UI. This creates confusion around the source of truth and makes deployment configuration brittle.

## 🎯 Objectives
- Establish `.env` as the exclusive source of truth for immutable system and security configurations.
- Establish the Settings UI (and its backend storage) as the exclusive source of truth for mutable user and behavior configurations.
- Unify the Chat UI's per-request settings with the global Settings UI to provide a cohesive user experience.

## 🛠 High-Level Approach
1. Define a strict separation schema classifying every configuration as either a "System/Security" setting (stays in `.env`) or a "User" setting (moves to Settings UI).
2. Remove user settings from `.env` and default them within the application code or the UI's storage backend instead.
3. Consolidate the frontend settings interface so that both global defaults and per-chat overrides share the same UI paradigm and underlying state management.

## ⚠️ Known Constraints / Risks
- **Migration:** Existing deployments currently rely on `.env` for some user settings. Dropping them from `.env` requires a fallback or migration script so they aren't lost upon upgrade.
- **Backward Compatibility:** API routes and schemas must be updated carefully to ensure the frontend doesn't break during the transition.

## ✅ Success Criteria
- [ ] Changing a user configuration via the Settings UI no longer conflicts with or relies on a `.env` value.
- [ ] `.env` contains strictly API keys, connection strings, and system-level parameters.
- [ ] All user-facing configuration options are accessible from the consolidated Setting page.

---
**Status:** 🟡 Awaiting Alignment
*(Move to 🟢 Aligned once user approves this proposal)*
