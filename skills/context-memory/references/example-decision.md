# Example Memory Promotion Decision

## Metadata

- Feature or investigation slug: `legacy-account-status-audit`
- Source artifact: `artifacts/features/legacy-account-status-audit/analysis.md`
- Reviewer: Maintainer example
- Date: 2026-05-01

## Candidate Finding

- Summary: Account status changes pass through the account-service domain layer before audit publishing.
- Why it might matter again: Future changes touching account lifecycle behavior need the same seam to avoid duplicating audit writes in adapters.

## Evidence

- Repository evidence: The analysis traced status mutations through the domain service and found downstream adapters only consume emitted events.
- Scope of evidence: Service layer, event publisher, and legacy admin path.
- What is still uncertain: Whether one deprecated batch import path still bypasses the service layer.

## Classification

- Decision: promote to `project-knowledge-base.md`
- Knowledge type: descriptive pattern
- Durability signal: Multiple account-status entrypoints share the same domain seam.

## Reason

- Why this destination fits: The finding is a stable architectural boundary, not a rule.
- Why the other destinations do not: It is not normative enough for the constitution and too reusable to leave only in one feature artifact.

## Follow-Up

- Owning next skill: `/project-knowledge-base`
- Concrete next action: Add one compact note describing the status-change seam and the deprecated import-path uncertainty.
