---
id: skill-visualize
name: visualize
description: ">-"
tags: ['visualization', 'diagrams', 'mermaid']
triggers: ['visualize', 'diagram', 'mermaid', 'chart']
next_skill: ''

---
# CoreZero Visualize

## Overview

Generate production-quality technical diagrams from natural language.
This is a specialist helper skill for plans, specs, and docs when a visual artifact genuinely improves clarity; it is not part of the default delivery loop.
Supported outputs in this repo: **SVG** (polished, deterministic) and **Mermaid** (editable text diagrams).

## I/O Hand-off Protocol

### Inputs
- Natural language diagram description from the user
- References: diagram style guides under `references/`

### Outputs
- SVG file, Mermaid code block, or both
- Validated against `scripts/validate-svg.sh` or `scripts/validate_mermaid.py`

### Next Skill
None (terminal — diagram output is embedded into documents by the caller)

This skill is not prompt-only. It ships with:
- `scripts/generate-from-template.py` for style-driven SVG generation
- `scripts/validate-svg.sh` for SVG validation
- `scripts/validate_mermaid.py` for Mermaid syntax validation
- `scripts/render_mermaid.py` for Mermaid-to-SVG rendering when `mmdc` is installed
- `templates/*.svg` starter templates

## Read First

- [formats-multi.md](references/formats-multi.md): Mermaid guidance and format notes. In this repo, Mermaid is implemented; PlantUML and draw.io are deferred.
- [style-1-flat-icon.md](references/style-1-flat-icon.md): Default white style.
- [style-2-dark-terminal.md](references/style-2-dark-terminal.md): Dark neon style.
- [style-3-blueprint.md](references/style-3-blueprint.md): Blueprint engineering style.
- [style-4-notion-clean.md](references/style-4-notion-clean.md): Minimal documentation style.
- [style-5-glassmorphism.md](references/style-5-glassmorphism.md): Frosted glass presentation style.
- [style-6-claude-official.md](references/style-6-claude-official.md): Warm Anthropic-like style.
- [style-7-openai.md](references/style-7-openai.md): Clean OpenAI-like style.
- [icons.md](references/icons.md): Semantic shapes and product icon guidance.

## Supported Outputs

| User intent | Emit |
|-------------|------|
| "generate diagram" | SVG |
| "polished" / "presentation" | SVG |
| "editable diagram" | SVG + Mermaid when the diagram maps cleanly to Mermaid |
| "mermaid" / "embed in GitHub" / "embed in Notion" | Mermaid |

Deferred in this repo:
- PlantUML generation
- draw.io XML generation
- PNG export
- interactive HTML wrappers

Do not claim deferred outputs as completed work.

## When to Use

- User requests a diagram explicitly ("draw a diagram", "visualize the flow", "create an architecture diagram")
- A spec, plan, or design doc would benefit from visual clarity
- Explaining system boundaries, data flow, or component relationships
- Documenting agent architecture, memory systems, or system coordination
- Creating sequence diagrams for API interactions or user flows
- Mapping state machines, decision trees, or process flows

**Do not use when:**
- The user only wants text-based documentation
- The description is too vague to resolve into nodes and edges
- A simple bullet list would be clearer than a diagram

## Workflow

1. **Classify** the diagram type.
2. **Choose output**: SVG by default; Mermaid when requested or appropriate.
3. **Extract structure**: nodes, containers, arrows, labels, and semantic groups.
4. **Load Style Reference**: Load `references/style-selection-guide.md` to pick the appropriate style. Default to `style-1-flat-icon.md` unless the guide indicates otherwise for the requested diagram context.
5. **Map shapes** using the semantic vocabulary below.
6. **Generate**:
   - For SVG, prefer `scripts/generate-from-template.py` with a fixture-like JSON payload.
   - For Mermaid, follow `references/formats-multi.md`.
7. **Validate**: Run the appropriate validator (SVG: run `scripts/validate-svg.sh <file.svg>`; Mermaid: run `python3 scripts/validate_mermaid.py <file.mmd>`). If validation fails:
   - Attempt one automated fix (correct the most common syntax error for the format).
   - Re-run the validator.
   - If it fails again → stop. Report the validation error verbatim. Do not deliver an invalid file. Write a `[GENERATION FAILED]` note with the error to the user.
8. **Optional render check**:
   - Mermaid to SVG: run `python3 scripts/render_mermaid.py <file.mmd> <file.svg>` if `mmdc` is available.
9. **Report absolute paths** of generated files.

## Diagram Types & Layout Rules

### Architecture Diagram
- Use horizontal layers: Client → Gateway/LB → Services → Data/Storage.
- Group related nodes with dashed containers.
- Route arrows through gaps, not through node interiors.

### Data Flow Diagram
- Label every arrow with the data type.
- Use wider strokes for primary data paths.
- Use dashed arrows for control and trigger flows.

### Flowchart / Process Flow
- Prefer top-to-bottom; use left-to-right for wide flows.
- Use diamonds for decisions and rounded rects for processes.
- Keep labels short.

### Agent Architecture Diagram
- Model the system in layers: Input, Agent Core, Memory, Tools, Output.
- Use loop arcs for iterative reasoning.

### Memory Architecture Diagram
- Separate read and write paths.
- Label key operations such as `store()`, `retrieve()`, and `consolidate()`.

### Sequence Diagram
- Use vertical lifelines and top-to-bottom time flow.
- Show activation boxes for active processing.

### Comparison / Feature Matrix
- Use compact columns and readable row spacing.
- Split into multiple diagrams when columns exceed five.

### Mind Map / Concept Map
- Center the root concept.
- Use curved branches instead of straight spokes.

### Class Diagram (UML)
- Three compartments: name, attributes, methods.
- Encode relationship types with standard UML arrowheads.

### Use Case Diagram (UML)
- Place actors outside the system boundary.
- Keep use case labels as verb phrases.

### State Machine Diagram (UML)
- Use rounded state boxes with initial/final markers.
- Label transitions as `event [guard] / action`.

### ER Diagram
- Use entity boxes with underlined PKs.
- Keep cardinality labels close to the related entity edge.

## Shape Vocabulary

| Concept | Shape |
|---------|-------|
| User / Human | Circle head + body path |
| LLM / Model | Rounded rect, double border |
| Agent / Orchestrator | Hexagon |
| Memory (short-term) | Dashed rounded rect |
| Memory (long-term) | Cylinder |
| Vector Store | Ringed cylinder |
| Graph DB | 3-circle cluster |
| Tool / Function | Rect with gear cue |
| API / Gateway | Smaller hexagon |
| Queue / Stream | Horizontal pipe |
| Document / File | Folded-corner rect |
| Browser / UI | Window rect with title bar |
| Decision | Diamond |
| External Service | Dashed rect |

## Arrow Semantics

| Flow Type | Meaning |
|-----------|---------|
| `control` | Main system control path |
| `read` | Retrieval or request path |
| `write` | Storage or writeback path |
| `data` | Data transformation path |
| `async` | Non-blocking or event flow |
| `feedback` | Loop or feedback path |

## SVG Rules

- Use system fonts only. No external font or icon fetches.
- Keep SVG XML valid and fully escaped.
- Prefer increased canvas size over dense packing.
- Add label backgrounds when overlap would reduce readability.
- Validate every generated SVG with `scripts/validate-svg.sh`.

## Mermaid Rules

- Prefer Mermaid for flowchart, sequence, class, state, ER, and mind map style outputs.
- Validate Mermaid with `scripts/validate_mermaid.py` before reporting success.
- If `mmdc` is unavailable, report that Mermaid syntax was validated structurally but not rendered.

## Output Rules

- Save SVG as `.svg`.
- Save Mermaid as `.mmd`.
- Use kebab-case file names.
- Always report absolute output paths.

**Output location**: Follow canonical paths from `../_shared/doc-conventions.md → ## Output Locations`.
- Feature-scoped: `artifacts/features/<slug>/diagrams/<name>.svg` (or `.mmd`)
- Global/standalone: `docs/generated/diagrams/<name>.svg` (or `.mmd`)

Validate Mermaid with:

```bash
source .venv/bin/activate
python3 ./skills/visualize/scripts/validate_mermaid.py path/to/diagram.mmd
```

## Core Rules

- **Semantic Shapes:** Use the shape vocabulary consistently (e.g., hexagons for agents, cylinders for databases).
- **Readable Labels:** Keep labels short (1-5 words). Use abbreviations when space is tight.
- **Arrow Semantics:** Label arrows with data types or flow names. Use dashed arrows for control/trigger flows.
- **Validation Required:** Always validate SVG with `scripts/validate-svg.sh` and Mermaid with `scripts/validate_mermaid.py`.
- **No External Dependencies:** SVG must use system fonts only. No external icon or font fetches.
- **Prefer Canvas Size Over Density:** Increase canvas size rather than cramming nodes together.
- **Style Consistency:** Default to `style-1-flat-icon.md` unless the user requests a specific style.
- **Mermaid for Editability:** Use Mermaid when the user wants to edit the diagram later or embed it in GitHub/Notion.
- **SVG for Polish:** Use SVG when the user wants a polished, presentation-ready diagram.

## Stop Conditions

- Ask for clarification when the description is too vague to resolve into nodes and edges.
- Do not generate a one-box diagram with no relationships.
