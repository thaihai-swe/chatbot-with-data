# Style Selection Guide

Use this guide to select the appropriate diagram style for the context. Default to style-1 when no other rule applies.

## Selection Rules

| Context | Style |
|---|---|
| Light-mode documentation (README, docs/) | `style-1-flat-icon.md` (default) |
| Presentations / slide decks | `style-7-openai.md` or `style-5-glassmorphism.md` |
| Dark-mode documentation or terminals | `style-2-dark-terminal.md` |
| Blueprint / engineering precision diagrams | `style-3-blueprint.md` |
| Sequence diagrams with many actors | `style-4-notion-clean.md` |
| Simple concept maps or mind maps | `style-1-flat-icon.md` |

## Override Rule

If the user explicitly requests a style by name or number, use that style regardless of context. Document the override in the generation report.
