# Chunk Upgrade — Notebook LM Alignment

## Current Phase: Implementing

## Complexity: Medium

## High-Level Progress
- [x] Research phase
- [x] Spec approved
- [x] Plan approved
- [ ] Implementation complete

## Intake
- Input type: `change_request`
- Risk flags: `data_model`, `cross_boundary`

## Triggered Domain Packs
- [x] RAG Pipeline
- [x] Document Ingestion

## Key Decisions Locked
- Full-doc injection chunks indexed to Weaviate
- Re-chunk is manual per-document
- Threshold = `max(1000, context_window_size * ratio)` with explicit override
- Embedding semantic has Jaccard fallback
- Old `chunking_strategy` overrides adaptive tiering

## Deliverables
- `spec.md`, `plan.md`, `tasks.md` — approved

## Next Step
Implement TASK-001 → TASK-002 → TASK-003 → TASK-004 → TASK-005
