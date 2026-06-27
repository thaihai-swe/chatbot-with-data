# Diagram Catalog

Mermaid diagram patterns shared across the documentation skills. Each skill picks from this catalog and adds its own preferences (which diagram is "primary," which supporting diagrams are common) in its SKILL.md.

## Selection Rules

- One diagram answers one question: flow, structure, data shape, or lifecycle.
- Pick the smallest diagram that makes the subject understandable.
- Split when one chart becomes crowded or mixes concerns.
- Replace a second diagram with a compact structured section (table, matrix) when it would otherwise add noise.
- Match diagrams to the written sections. If they disagree, fix the document.
- Show only the branches that materially help the reader. Add error or auth branches only when they change understanding.

## Sequence diagram — order of interactions

Use when the order of handoffs matters, a workflow crosses layers or services, or you need to show request/response/event handoffs.

```mermaid
sequenceDiagram
    actor User
    participant API
    participant Service
    participant DB
    participant Bus as Event Bus

    User->>API: Submit order
    API->>Service: Validate and create
    Service->>DB: Insert order
    DB-->>Service: Order row
    Service->>Bus: Publish OrderCreated
    Service-->>API: Created order
    API-->>User: 201 Created
```

## Flowchart — branching logic

Use when decisions matter more than timing, validation or policy checks short-circuit processing, or alternate error paths are central.

```mermaid
flowchart TD
    A[Request received] --> B{Authenticated?}
    B -- No --> C[Return 401]
    B -- Yes --> D{Payload valid?}
    D -- No --> E[Return 400]
    D -- Yes --> F[Run workflow]
    F --> G[Persist and respond]
```

## System context / container view — boundaries

Use when readers need to understand component ownership, the system talks to multiple downstream services, or architectural complexity is the main risk.

```mermaid
flowchart LR
    Client[Client App] --> Gateway[API Gateway]
    Gateway --> App[Core Service]
    App --> DB[(Primary DB)]
    App --> Cache[(Cache)]
    App --> Billing[Billing Service]
    App --> Queue[Job Queue]
```

## ERD — data shape

Use when shared entities shape the workflows, readers need to understand relationships, or payload/persistence design is central.

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : appears_in
```

## State diagram — lifecycle

Use when a resource moves through explicit phases, behavior changes by state, or jobs/sessions/orders have meaningful transitions.

```mermaid
stateDiagram-v2
    [*] --> Pending
    Pending --> Running : start
    Running --> Succeeded : complete
    Running --> Failed : error
    Failed --> Pending : retry
    Succeeded --> [*]
```

## Class / domain model — entity behavior

Use when methods on entities matter, inheritance or composition shapes the design, or readers need a typed contract.

```mermaid
classDiagram
    class User {
        +String id
        +String email
        +login()
        +logout()
    }
    class Order {
        +String id
        +Number total
        +submit()
        +cancel()
    }
    User "1" --> "*" Order
```

## Deployment / infrastructure view — runtime topology

Use when readers need to understand how the system is deployed, replication or load balancing is central, or the docs cover ops handoff.

```mermaid
flowchart TB
    LB[Load Balancer] --> App1[App 1]
    LB --> App2[App 2]
    App1 --> Primary[(Primary DB)]
    App2 --> Primary
    Primary -.->|replication| Replica[(Replica)]
    App1 --> Cache[(Redis)]
    App2 --> Cache
```
