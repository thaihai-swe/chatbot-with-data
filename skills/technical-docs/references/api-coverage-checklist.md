# Coverage Checklist

Use this checklist before you finalize API docs.

## Core Reference Coverage

- Service or module name
- Intended audience
- Scope boundaries
- Base path or version prefix when present
- Endpoint summary table
- Detailed endpoint coverage for each route in scope

## Contract Coverage

- Authentication and authorization rules
- Path, query, header, and body inputs
- Success and failure status codes
- Response body shape
- Shared error envelope or error vocabulary
- Side effects such as events, notifications, cache invalidation, or writes

## Example Coverage

- At least one concrete request example
- At least one concrete success response example
- Error example when the code or existing docs support it
- Note missing examples explicitly when the source does not support safe reconstruction

## Supporting Context Coverage

- Shared middleware behavior
- Pagination, filtering, sorting, or cursor rules
- Rate limiting, idempotency, retries, or timeouts when relevant
- External dependencies or downstream services
- Data model notes for important request or response entities
- Deprecation or versioning notes when observable

## Visual Coverage

- One primary request-flow diagram
- One supporting diagram for non-trivial APIs, chosen from:
  - System context or container view
  - Authentication flow
  - ERD or data model
  - State diagram for resource lifecycle
  - Focused dependency diagram

## Trust Checks

- Facts are traceable to source
- Unknowns are labeled
- Examples do not invent unsupported details
- The document helps a reader understand the API without reading implementation code first
