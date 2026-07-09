# Architecture Rules

> Normative rules for structural design, separation of concerns, and domain modeling.
> Load this file when making architectural choices, defining new entities, or structuring layers.

## Principles

### Clean Architecture
- **Dependency Rule:** Source code dependencies must point inward, toward higher-level policies (domain). Inner circles (domain/entities) must know nothing about outer circles (DB, UI, frameworks).
- **Separation of Concerns:** Keep business rules isolated from UI and Database. Never pass a database cursor or HTTP request object into the domain layer.
- **Interfaces (Ports & Adapters):** When the domain needs to communicate with the outside world, use interfaces defined in the domain layer. The outer layer implements these interfaces.
- **Anti-Patterns:** Layering Violation (e.g., domain logic directly importing and calling a specific DB driver); Anemic Domain Model (services holding all logic while entities are just getters/setters).

### Domain-Driven Design (DDD)
- **Ubiquitous Language:** Use the exact terminology from the `glossary.md` in your code (classes, variables, methods). Do not translate terms.
- **Aggregates:** Group related entities into an aggregate with a single root. All modifications must go through the aggregate root to enforce invariants.
- **Value Objects:** Prefer immutable value objects (e.g., `Money(amount, currency)`) over primitives when the primitive has business meaning or rules.
- **Domain Services:** Use domain services for operations that do not naturally belong to a single entity or value object, but still encapsulate business rules.
- **Anti-Patterns:** Primitive Obsession (using plain strings or ints instead of Value Objects for structured concepts); Missing Aggregate Root (allowing direct modification of child entities bypassing the root's invariants).

### SOLID Principles
- For SOLID enforcement rules, see `rules/code-design.md` § Practical SOLID.
