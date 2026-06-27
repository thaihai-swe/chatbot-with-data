# API Endpoint Document Template

Use this structure unless the user asked for a different format.

## 1. Audience and Scope

- Who this document is for
- What service or module this document covers
- Which routes are included or excluded
- Where the facts came from: code, OpenAPI spec, README, tests

## 2. API Overview

- Base path or version prefix
- High-level purpose of the API area
- Shared conventions that affect many endpoints

## 3. Quick Start Example

Start with one minimal example that helps a reader make a successful request quickly when the source supports it.

## 4. Primary Request Flow Diagram

Start with at least one Mermaid diagram that explains the main request lifecycle.

Recommended summary table:

| Method | Path | Handler | Auth | Summary |
| --- | --- | --- | --- | --- |
| GET | `/example` | `getExample` | Required | Return example resource |

## 5. Supporting Diagram or Supporting Structured Section

Add one of these when the system is non-trivial:

- System context or container diagram
- Authentication flow
- ERD or data model diagram
- Resource lifecycle state diagram
- Dependency map
- Auth matrix or shared data model table if a second diagram would be noise

## 6. Endpoint Details

Repeat this section for each endpoint:

### `METHOD /path`

**Purpose**
- One or two sentences on what the endpoint does

**Entry Point**
- Router or controller entry

**Authentication / Authorization**
- Required auth
- Role or permission checks

**Inputs**
- Path params
- Query params
- Headers
- Body schema
- Validation rules or important constraints

**Processing**
- Validation or middleware
- Main service calls
- Data reads and writes
- External integrations

**Responses**
- Success status codes and body shape
- Error status codes and when they happen
- Response headers when important

**Examples**
- Example request
- Example success response
- Example error response when available

**Side Effects**
- Mutations, events, notifications, cache changes, audit logs

**Dependencies**
- Databases, queues, third-party services, internal services

**Notes**
- Assumptions, gaps, or conflicts with pre-existing docs

## 7. Shared Behavior

Add a short section for shared middleware, auth, pagination, rate limits, or error envelopes when those affect multiple endpoints.

## 8. Data Models and Shared Contracts

Summarize important request or response objects, enums, and shared schemas when they appear across endpoints.

## 9. Error Model

Summarize common error shapes, codes, and retry guidance when shared across endpoints.

## 10. Operational Notes

Capture versioning, deprecations, idempotency, retries, caching, eventual consistency, webhooks, or downstream dependency caveats when relevant.

## 11. Open Questions

List unresolved points only when they affect correctness or reader trust.
