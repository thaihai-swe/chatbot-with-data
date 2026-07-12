# ADR-001: Example Decision

Status: Accepted
Date: 2026-06-23
Deciders: CoreZero Maintainers
Feature slug: none
Related spec: none
Related plan: none

## Context
Adopter repositories require a starting architecture decision template and example to understand the format and usage of the ADR loop.

## Decision
We will ship a standard example ADR (ADR-001) inside the kit to demonstrate the layout and structure of the Architecture Decision Records.

## Options Considered

### Option A: Clean index with no example
* Pros: Leaves the adopter repository entirely clean.
* Cons: Provides no guidance on the expected format of an ADR file.

### Option B: Ship 0001-example.md
* Pros: Acts as a seeded template and concrete reference.
* Cons: The adopter has an extra file, which they can later clean up or mark as superseded.

## Trade-off Analysis
Option B is selected because having a concrete example reduces setup friction and prevents format drift in downstream repositories.

## Consequences
* Adopters have a clear template.
* No manual styling guesses are required.
