# Feature Artifacts

Each feature gets a subdirectory under `artifacts/features/<slug>/`. Below are all standard artifacts, their tier, location, owning skill, phase of creation, and schema reference.

| Artifact | Tier | Location | Owning skill | Phase | Schema |
|---|---|---|---|---|---|
| `status.md` | Durable | `artifacts/features/<slug>/` | spec-research / all | All | `_shared/status-template.md` |
| `analysis.md` | Durable | `artifacts/features/<slug>/` | spec-research | Researching | `spec-research/references/analysis-template.md` |
| `proposal.md` | Durable | `artifacts/features/<slug>/` | spec-requirements | Spec'ing | `spec-requirements/references/proposal-template.md` |
| `spec.md` | Durable | `artifacts/features/<slug>/` | spec-requirements | Spec'ing | `spec-requirements/references/spec-template.md` |
| `plan.md` | Durable | `artifacts/features/<slug>/` | spec-plan | Planning | `spec-plan/references/plan-template.md` |
| `tasks.md` | Durable | `artifacts/features/<slug>/` | spec-plan | Planning | `spec-plan/references/tasks-template.md` |
| `progress.md` | Ephemeral | `.corezero/sessions/<slug>/` | spec-implement / context-session | Implementing | `context-session/references/progress-template.md` |
| `handoff.md` | Ephemeral | `.corezero/sessions/<slug>/` | context-session | Session End | `context-session/references/session-handoff-template.md` |
| `session-extracts.md` | Semi-durable | `artifacts/features/<slug>/` | spec-implement / context-session | Implementing+ | `context-session/references/session-extracts-template.md` |
| `requirements-review.md` | Semi-durable | `artifacts/features/<slug>/` | spec-requirements | Spec'ing | `spec-requirements/references/requirements-review-template.md` |
| `review.md` | Durable | `artifacts/features/<slug>/` | harness-verify / code-review | Verifying | `harness-verify/references/review-template.md` |
| `testing-scenarios.md` | Durable | `artifacts/features/<slug>/` | harness-verify | Verifying | `harness-verify/references/testing-scenarios-template.md` |
| `promotions.md` | Durable | `artifacts/features/<slug>/` | context-memory | Memory Sync | (proposal, free-form) |
| `memory-audit.md` | Durable | `artifacts/features/<slug>/` | context-memory --audit | Memory Sync | (audit report) |

**Complexity Notes:**
- `proposal.md` — generated for Moderate/Complex only.

## Lifecycle

- **Ephemeral files** (`progress.md`, `handoff.md`) are deleted by `context-status` GC when the feature reaches `Done` AND `session-extracts.md` has been triaged. They are gitignored and not committed.
- **Durable files** are never auto-deleted. They remain as historical record.
- **Semi-durable files** (`session-extracts.md`, `requirements-review.md`) are retained until manually cleaned or triaged.
