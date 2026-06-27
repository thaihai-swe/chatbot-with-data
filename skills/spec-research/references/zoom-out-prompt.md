# Zoom-Out Prompt

A canned prompt for stepping up a level of abstraction when research is too deep in implementation detail.

## When to Use

- The user (or you) is lost in file-level detail and has lost the shape of the system.
- Findings are growing without converging on a decision.
- You are about to recommend a change but cannot name the surrounding callers, contracts, or boundaries.
- A new contributor is being onboarded to a subsystem.

## The Prompt

> Go up a layer of abstraction. Give me a map of the relevant modules and callers, using the project's domain glossary vocabulary. Name:
>
> 1. The 3-7 modules that matter for this question, and what each one owns.
> 2. The callers that cross the boundary into those modules.
> 3. The data or contracts that flow between them.
> 4. The terms from `docs/project/glossary.md` (or `memories/repo/project-knowledge-base.md`) that name what is happening.
>
> Skip line-level detail. Skip files that are not on the critical path. The goal is a one-screen map that lets the next decision get made without re-reading the code.

## Rules

- *Vocabulary discipline:* Use glossary terms when they exist. Coining new names for existing concepts is a research smell.
- *One-screen ceiling:* If the map does not fit on one screen, the abstraction is still too low.
- *Cite, don't invent:* Every module named in the map must be backed by a real path. Inferred boundaries should be marked as inferred.
- *Pair with a decision:* A zoom-out is a means, not the end. Name the decision the map should unblock.

## Anti-Patterns

| Anti-Pattern | Why It's Bad |
|---|---|
| Listing every file in a directory | That's an inventory, not a map. |
| Naming abstractions the codebase doesn't actually use | Invents debt instead of describing reality. |
| Producing the map but not the decision it unblocks | Zoom-out becomes performative — research without convergence. |

## Output

The output of a zoom-out belongs in `analysis.md` under a `## System Map` section, or pasted inline into the conversation as scaffolding for the next decision.
