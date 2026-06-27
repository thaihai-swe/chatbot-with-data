# Multi-Format Output Reference

This reference is broader than the currently implemented repo scope.

Implemented in `skills/visualize`:
- SVG
- Mermaid

Deferred in this repo:
- PlantUML
- draw.io XML
- DOT / Graphviz

## Format Selection Guide

| Goal | Use Format |
|------|-----------|
| Polished visual for presentation / README / docs | SVG |
| Embed in GitHub markdown, Notion, Obsidian | Mermaid |
| UML diagrams with full notation (sequence, class, activity) | PlantUML |
| Graphical editing in diagrams.net (free browser tool) | draw.io XML |
| Dependency graphs, DAGs | DOT / Graphviz |

**Default behavior:** emit SVG. Add Mermaid when the diagram type is supported and the user wants an editable text format.
Mermaid-unsupported types (Agent Architecture, Memory Architecture, Comparison Matrix, Network Topology, Timeline) → SVG only.

---

## Mermaid Syntax by Diagram Type

### Flowchart / Process Flow

```mermaid
flowchart TD
    A([Start]) --> B[Step One]
    B --> C{Decision?}
    C -- yes --> D[Path A]
    C -- no --> E[Path B]
    D --> F([End])
    E --> F

    style A fill:#10b981,stroke:#059669,color:#fff
    style F fill:#10b981,stroke:#059669,color:#fff
```

**Shapes:**
- `([text])` — stadium/pill → start/end
- `[text]` — rectangle → process
- `{text}` — diamond → decision
- `[(text)]` — cylinder → database
- `[[text]]` — double-bordered → subprocess
- `>text]` — flag → document

**Direction options:** `TD` (top-down), `LR` (left-right), `BT`, `RL`

---

### Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant A as Agent
    participant L as LLM
    participant T as Tool

    U->>A: query
    activate A
    A->>L: prompt + context
    activate L
    L-->>A: tool_call(search)
    deactivate L
    A->>T: execute search
    T-->>A: results
    A->>L: results + prompt
    activate L
    L-->>A: final response
    deactivate L
    A-->>U: answer
    deactivate A

    Note over A,L: Agentic loop — may repeat
```

**Arrow types:**
- `->>` solid arrow with filled head
- `-->>` dashed arrow with filled head
- `-x` solid arrow with X head (async)
- `--x` dashed arrow with X head

---

### Architecture Diagram (C4 — System Context)

```mermaid
C4Context
    title System Context — CoreZero

    Person(user, "Developer", "Uses AI agent to build features")
    System(corezero, "AI Agents Dev Kit", "Skill-driven spec → code workflow")
    System_Ext(llm, "LLM (Claude / Gemini)", "Executes skill instructions")
    SystemDb(artifacts, "Artifacts (Git)", "Durable state: spec, plan, tasks")

    Rel(user, corezero, "Runs public commands via the pack-based workflow")
    Rel(corezero, llm, "Reads skills, delegates tasks")
    Rel(llm, artifacts, "Writes spec.md, plan.md, tasks.md")
    Rel(user, artifacts, "Reviews and approves")
```

**C4 element types:**
- `Person(alias, label, desc)` — user/actor
- `System(alias, label, desc)` — internal system
- `System_Ext(alias, label, desc)` — external system
- `SystemDb(alias, label, desc)` — data store
- `Container(alias, label, tech, desc)` — container
- `Component(alias, label, tech, desc)` — component

---

### State Machine

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> UnderReview : submit()
    UnderReview --> Approved : approve()
    UnderReview --> Draft : request_changes()
    Approved --> Locked : lock()
    Locked --> [*]

    state UnderReview {
        [*] --> WaitingPeer
        WaitingPeer --> PeerApproved : peer_approves()
    }
```

---

### ER Diagram

```mermaid
erDiagram
    FEATURE {
        string slug PK
        string title
        string status
        datetime created_at
    }
    ARTIFACT {
        string id PK
        string slug FK
        string type
        string path
    }
    TASK {
        string id PK
        string slug FK
        string description
        boolean done
    }

    FEATURE ||--o{ ARTIFACT : "has"
    FEATURE ||--o{ TASK : "decomposes into"
```

**Cardinality:**
- `||--||` exactly one to exactly one
- `||--o{` exactly one to zero or many
- `}o--o{` zero or many to zero or many
- `|{--||` one or many to exactly one

---

### Class Diagram

```mermaid
classDiagram
    class Skill {
        +String name
        +String description
        +List~String~ references
        +execute(context) Result
    }

    class ArtifactWriter {
        +String basePath
        +write(name, content) void
        +read(name) String
    }

    class SkillRunner {
        -Skill skill
        -ArtifactWriter writer
        +run(prompt) Result
    }

    Skill <|-- DiagramSkill
    SkillRunner --> Skill : uses
    SkillRunner --> ArtifactWriter : writes via
    DiagramSkill --> ArtifactWriter : writes SVG/Mermaid
```

---

### Mind Map

```mermaid
mindmap
  root((CoreZero))
    Context
      Memory
        constitution.md
        knowledge-base.md
      Research
        analysis.md
    Definition
      Spec
        proposal.md
        spec.md
      Diagram
        SVG + Mermaid
      ADR
        adr-N.md
    Execution
      Plan
        tasks.md
      Implement
      Verify
        review.md
    Continuity
      Session End
      Handoff
        handoff.md
```

---

### User Journey (Mermaid only, not in SVG skill)

```mermaid
journey
    title Developer Feature Workflow
    section Understand
      Run status: 5: Developer
      Read constitution: 4: Developer, Agent
      Research codebase: 3: Agent
    section Define
      Answer grilling questions: 4: Developer
      Review spec.md: 5: Developer
      Approve diagram: 4: Developer
    section Build
      Review tasks.md: 4: Developer
      Monitor implementation: 3: Developer
      Run verify: 5: Developer, Agent
```

---

### Gantt / Timeline (Mermaid only, not in SVG skill yet)

```mermaid
gantt
    title CoreZero Feature Delivery Timeline
    dateFormat YYYY-MM-DD
    section Context
    Memory & Research     :a1, 2025-01-01, 1d
    section Definition
    Spec & Diagram        :a2, after a1, 2d
    ADR                   :a3, after a2, 1d
    section Execution
    Plan                  :a4, after a3, 1d
    Implement             :a5, after a4, 3d
    Verify                :a6, after a5, 1d
    section Continuity
    Session Closeout      :a7, after a6, 1d
```

---

## PlantUML Syntax by Diagram Type

PlantUML handles UML diagrams better than Mermaid. Use for sequence diagrams with complex logic, class diagrams with many relationships, and activity diagrams.

### Sequence Diagram (PlantUML)

```plantuml
@startuml
autonumber
skinparam backgroundColor #0f0f1a
skinparam sequence {
  ArrowColor #a855f7
  LifeLineBorderColor #334155
  ParticipantBorderColor #334155
  ParticipantBackgroundColor #0f172a
  ParticipantFontColor #e2e8f0
}

actor User as U
participant "Agent" as A
participant "LLM" as L
database "VectorDB" as V

U -> A: query
activate A
A -> L: embed(query)
L --> A: embedding
A -> V: search(embedding, top_k=5)
V --> A: chunks[]
A -> L: generate(query + chunks)
L --> A: response
A --> U: answer
deactivate A

@enduml
```

### Class Diagram (PlantUML)

```plantuml
@startuml
class Skill {
  +name: String
  +description: String
  +execute(ctx: Context): Result
}

class DiagramSkill {
  +formats: List<Format>
  +styles: List<Style>
  +generate(desc: String): DiagramOutput
}

class DiagramOutput {
  +svg: String
  +mermaid: String
  +plantuml: String
}

Skill <|-- DiagramSkill
DiagramSkill ..> DiagramOutput : creates
@enduml
```

### Activity Diagram / Flowchart (PlantUML)

```plantuml
@startuml
start
:Read status.md;
:Classify diagram type;
if (type known?) then (yes)
  :Load style reference;
  :Generate SVG;
  :Generate Mermaid;
  :Validate XML;
else (no)
  :Ask for clarification;
  stop
endif
:Write files;
:Report paths;
stop
@enduml
```

---

## draw.io XML (diagrams.net)

Use when the user needs to edit the diagram graphically. Output the XML inside a code block; user saves as `.drawio` and opens in https://app.diagrams.net.

### Minimal draw.io Template

```xml
<mxfile>
  <diagram name="Page-1">
    <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" tooltips="1"
                  connect="1" arrows="1" fold="1" page="1" pageScale="1"
                  pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <!-- Node example -->
        <mxCell id="2" value="Component A" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="100" y="100" width="160" height="60" as="geometry"/>
        </mxCell>

        <!-- Node example -->
        <mxCell id="3" value="Component B" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="340" y="100" width="160" height="60" as="geometry"/>
        </mxCell>

        <!-- Arrow -->
        <mxCell id="4" value="calls" style="edgeStyle=orthogonalEdgeStyle;" edge="1" source="2" target="3" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

---

## Output Rules (Multi-Format)

When generating a diagram, produce outputs in this priority order:

1. **SVG** — always (main output, polished visual)
2. **Mermaid** — when the diagram type is supported by Mermaid syntax
3. **PlantUML** — for UML types (Class, Sequence, State, Activity, Use Case) when user requests editable UML
4. **draw.io XML** — only when user explicitly asks for "editable" or "draw.io"

Never force all formats simultaneously — match the user's goal.

### File Naming Convention

```
my-diagram.svg          # SVG output (always)
my-diagram.mmd          # Mermaid source (when applicable)
my-diagram.puml         # PlantUML source (when applicable)
my-diagram.drawio       # draw.io XML (when requested)
```

### Embed in Markdown

**Mermaid in markdown:**
````markdown
```mermaid
flowchart TD
    A --> B
```
````

**SVG inline in markdown:**
```markdown
![Diagram Title](./my-diagram.svg)
```

**PlantUML** — requires a server or plugin:
```markdown
<!-- in systems with PlantUML support -->
@startuml
A -> B
@enduml
```
