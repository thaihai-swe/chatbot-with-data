---
name: aiddk-diagram
description: Transform complex technical concepts (architecture, flows, data models) into professional Mermaid diagrams. Use when the user needs to visualize systems, processes, or decisions.
compatibility: Designed for all Agent Skills-compatible tools.
metadata:
  author: gemini-cli
---

# Kit Diagram

## Overview

The `aiddk-diagram` skill transforms technical descriptions, specifications, or codebase structures into clear, maintainable, and version-controlled text-based diagrams using Mermaid syntax.

## Read First

- `artifacts/features/<slug>/status.md`
- [flowcharts.md](references/flowcharts.md): Process flows, algorithms, and journeys.
- [c4-diagrams.md](references/c4-diagrams.md): System architecture (Context, Container, Component).
- [sequence-diagrams.md](references/sequence-diagrams.md): Temporal interactions and API flows.
- [state-diagrams.md](references/state-diagrams.md): Object lifecycles and behavior flows.
- [user-journey.md](references/user-journey.md): User experience and friction points.
- [mindmaps.md](references/mindmaps.md): Brainstorming and hierarchical mapping.
- [erd-diagrams.md](references/erd-diagrams.md): Database schema and data modeling.
- [class-diagrams.md](references/class-diagrams.md): OO design and domain modeling.
- [advanced-features.md](references/advanced-features.md): Themes, styling, and config.

## When to Use

- **Architecture Reviews:** Visualizing system boundaries and dependencies (C4).
- **Process Mapping:** Documenting complex logic or user journeys (Flowchart).
- **Behavior Modeling:** Defining state transitions and lifecycles (State).
- **UX Alignment:** Mapping the user path and identifying friction (User Journey).
- **Brainstorming:** Organizing thoughts during research or discovery (Mindmap).
- **Database Design:** Modeling entity relationships (ERD).
- **Communication:** Illustrating API interactions or distributed system events (Sequence).

## Workflow

1. **Context Check:** Read `status.md` to understand the current phase.
2. **Analyze Source:** Review the `spec.md`, `analysis.md`, or relevant source code to identify key actors, systems, and relationships.
3. **Select Diagram Type:** Choose the most appropriate Mermaid type based on the goal (e.g., C4 for high-level architecture, Sequence for detailed timing).
4. **Draft Syntax:** Create the Mermaid code block. Use meaningful IDs and descriptive labels.
5. **Annotate:** Add internal documentation using `%%` comments to explain complex logic within the diagram.
6. **Finalization:** Update `status.md` if the diagram resolves a specific blocker or completes a visualization task.

## Stop Conditions

- **Trivial Logic:** Do not create diagrams for simple "if/else" blocks that are easily readable in code.
- **Context Missing:** Halt if the source technical description is too vague to form a coherent visualization.

## Core Rules

- **DRY Diagrams:** Keep diagrams focused on a specific layer or flow; do not try to visualize everything in one chart.
- **Directional Consistency:** Use `TD` (Top-Down) or `LR` (Left-Right) consistently to optimize for the expected medium (e.g., mobile-friendly docs prefer `TD`).
- **Standard Symbols:** Adhere to the shapes and connection styles defined in the reference guides.

## Rationalization vs. Reality

| Rationalization | Reality |
|---|---|
| "The code is the documentation." | Code explains 'how', diagrams explain 'how it fits together'. Visuals provide immediate mental models that code cannot replicate at scale. |
| "Diagrams get out of date too fast." | Mermaid diagrams as code are easy to update and provide high-level context that code alone lacks. |
| "I don't have time to make it pretty." | Clarity of flow matters more than aesthetics. A rough Mermaid chart is better than no mental map. |

## Red Flags
- **Spaghetti Diagrams:** Too many crossing lines or nodes indicate the diagram should be split into multiple subgraphs or separate files.
- **Outdated Labels:** Using variable names or IDs that don't match the current `spec.md` or codebase.

## Verification

Before finalizing, verify:
- [ ] Does the diagram accurately reflect the current technical state or proposed spec?
- [ ] Is the Mermaid syntax valid?
- [ ] Are internal comments (`%%`) used to explain non-obvious relationships?

## Output Rules

- **Standard Output:** Provide the diagram within a triple-backtick markdown block tagged with `mermaid`.
- **File Placement:** If requested to save, place diagrams in `artifacts/features/<slug>/` or adjacent to the relevant `spec.md`.
