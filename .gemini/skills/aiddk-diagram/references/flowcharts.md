# Flowcharts

Flowcharts are used to represent processes, algorithms, and workflows.

## Syntax Overview

- **Direction**: `flowchart TD` (Top-Down), `flowchart LR` (Left-Right), `flowchart BT` (Bottom-Top), `flowchart RL` (Right-Left).
- **Nodes**:
    - `id[Rectangle]`: Standard process.
    - `id([Stadium])`: Start/End.
    - `id[[Subroutine]]`: Predefined process.
    - `id[(Cylinder)]`: Database.
    - `id{Rhombus}`: Decision.
    - `id{{Hexagon}}`: Preparation.
    - `id[/Parallelogram/]`: Input/Output.
- **Connections**:
    - `A --> B`: Arrow.
    - `A --- B`: Line.
    - `A -- Text --> B`: Arrow with text.
    - `A -.-> B`: Dotted arrow.
    - `A ==> B`: Thick arrow.
    - `A --o B`: Circle end.
    - `A --x B`: Cross end.

## Examples

### User Authentication Flow
```mermaid
flowchart TD
    Start([Start]) --> Login[Enter Credentials]
    Login --> Valid{Valid?}
    Valid -- No --> Error[Show Error]
    Error --> Login
    Valid -- Yes --> MFA{MFA Enabled?}
    MFA -- Yes --> Verify[Verify Token]
    Verify --> Success([Authenticated])
    MFA -- No --> Success
```

### CI/CD Pipeline
```mermaid
flowchart LR
    Push[Push Code] --> Build[Build]
    Build --> Test[Unit Tests]
    Test --> Lint[Linting]
    Lint --> Deploy{Deploy to Staging?}
    Deploy -- Yes --> Staging[Staging Env]
    Deploy -- No --> Done([Done])
    Staging --> Approve{Manual Approval?}
    Approve -- Yes --> Prod[Production Env]
    Approve -- No --> Done
```

## Advanced Features

### Subgraphs
```mermaid
flowchart TB
    c1-->a2
    subgraph one [First Group]
    a1-->a2
    end
    subgraph two [Second Group]
    b1-->b2
    end
    subgraph three [Third Group]
    c1-->c2
    end
```

### Styling Nodes
```mermaid
flowchart LR
    id1(Start)-->id2(Stop)
    style id1 fill:#f9f,stroke:#333,stroke-width:4px
    style id2 fill:#bbf,stroke:#f66,stroke-width:2px,color:#fff,stroke-dasharray: 5 5
```
