# Diagram Patterns

See [diagram-catalog.md](../../../_shared/diagram-catalog.md) for available Mermaid structures.

These are larger, project-shaped patterns that combine multiple base diagrams.

## Layered Architecture

Use for monolithic apps with clear presentation/business/data layers.

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI[User Interface]
        Controllers[Controllers]
    end

    subgraph "Business Logic Layer"
        Services[Services]
        Domain[Domain Models]
    end

    subgraph "Data Access Layer"
        Repositories[Repositories]
        ORM[ORM/Data Mappers]
    end

    subgraph "Infrastructure"
        DB[(Database)]
        Cache[(Cache)]
        Queue[Message Queue]
    end

    UI --> Controllers
    Controllers --> Services
    Services --> Domain
    Services --> Repositories
    Repositories --> ORM
    ORM --> DB
    Services --> Cache
    Services --> Queue
```

## Microservices Topology

Use when documenting service boundaries, gateways, and per-service data stores.

```mermaid
graph TB
    subgraph "API Gateway"
        Gateway[API Gateway]
    end

    subgraph "Services"
        Auth[Auth Service]
        User[User Service]
        Order[Order Service]
        Payment[Payment Service]
    end

    subgraph "Data Stores"
        AuthDB[(Auth DB)]
        UserDB[(User DB)]
        OrderDB[(Order DB)]
    end

    subgraph "Infrastructure"
        Cache[(Redis)]
        Queue[Message Queue]
    end

    Gateway --> Auth
    Gateway --> User
    Gateway --> Order
    Gateway --> Payment

    Auth --> AuthDB
    User --> UserDB
    Order --> OrderDB

    Order --> Queue
    Payment --> Queue
    User --> Cache
```

## ETL Pipeline

Use for data pipeline projects with extract/transform/load stages.

```mermaid
graph LR
    subgraph "Extract"
        Source1[(Source DB 1)]
        Source2[(Source DB 2)]
        API[External API]
    end

    subgraph "Transform"
        Clean[Data Cleaning]
        Validate[Validation]
        Enrich[Enrichment]
    end

    subgraph "Load"
        Warehouse[(Data Warehouse)]
        Cache[(Cache)]
    end

    Source1 --> Clean
    Source2 --> Clean
    API --> Clean
    Clean --> Validate
    Validate --> Enrich
    Enrich --> Warehouse
    Enrich --> Cache
```

## Cloud Deployment Topology

Use for DEPLOYMENT.md when documenting load balancers, app tiers, and replicated data.

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Application Load Balancer]
    end

    subgraph "Application Tier"
        App1[App Server 1]
        App2[App Server 2]
        App3[App Server 3]
    end

    subgraph "Data Tier"
        Primary[(Primary DB)]
        Replica1[(Replica 1)]
        Replica2[(Replica 2)]
    end

    subgraph "Cache Tier"
        Redis[(Redis Cluster)]
    end

    LB --> App1
    LB --> App2
    LB --> App3

    App1 --> Primary
    App2 --> Primary
    App3 --> Primary

    App1 --> Replica1
    App2 --> Replica2

    App1 --> Redis
    App2 --> Redis
    App3 --> Redis

    Primary -.->|Replication| Replica1
    Primary -.->|Replication| Replica2
```

## Tips for Codebase Diagrams

1. **Match the actual structure.** Use the names and groupings that exist in the codebase, not generic placeholders.
2. **Subgraph by responsibility.** Group services, layers, or tiers — not files.
3. **Show the main paths.** Highlight golden-path flows; leave edge cases for prose.
4. **Label arrows with intent.** "Replication," "publishes event," "reads from cache" — not just lines.
5. **Test rendering.** Verify diagrams render in the target viewer (GitHub, docs site).
