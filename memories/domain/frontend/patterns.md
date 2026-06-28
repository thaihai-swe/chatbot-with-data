# Frontend UI — Patterns

> **Ownership:** Collaborative — skill-updated + user-maintained.

## Screen-Component Separation

**When to use:** When building new UI pages.

**Key implementation notes:**
- Screens own page-level state, routing, and data fetching
- Components are reusable, receive data via props, and are screen-agnostic
- API calls happen at the screen level, not in components

**Citation:** `frontend/src/screens/` contains 7 screens; `frontend/src/components/` contains 13 reusable components.

---

## API Client Module Pattern

**When to use:** When adding new backend API interactions.

**Key implementation notes:**
- Each domain area gets its own API module under `frontend/src/api/`
- Modules export functions that return promises
- Base client configuration (base URL, headers, error handling) lives in `client.js`
- Screens import only the modules they need

**Citation:** `frontend/src/api/client.js` provides base configuration; domain modules (`chat.js`, `knowledgeApi.js`, `settings.js`) extend it.

---

## Dev Proxy for Local Development

**When to use:** When running frontend in dev mode against the backend.

**Key implementation notes:**
- Vite dev proxy is configured in `vite.config.js` to forward API requests to `localhost:8000`
- No CORS issues in dev mode because the proxy handles routing
- Production builds would need explicit API URL configuration

**Citation:** `frontend/vite.config.js` contains the proxy configuration.
