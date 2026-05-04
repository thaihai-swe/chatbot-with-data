# Example Traceability Audit

## Metadata

- Feature slug: `magic-link-login`
- Auditor: Maintainer example
- Date: 2026-05-01
- Artifact set reviewed: `spec.md`, `plan.md`, `tasks.md`, `review.md`

## Coverage Summary

- Overall status: partial
- Short summary: Core login issuance and verification tasks are traceable, but session-expiry regression evidence is not yet linked to one completed task.

## REQ -> AC Coverage

- REQ-001:
  Linked AC(s): `AC-001`, `AC-002`
  Status: complete
- REQ-002:
  Linked AC(s): `AC-003`
  Status: complete

## AC -> TASK Coverage

- AC-001:
  Linked TASK(s): `TASK-001`, `TASK-002`
  Status: complete
- AC-003:
  Linked TASK(s): `TASK-004`
  Status: partial

## TASK -> Validation Coverage

- TASK-001:
  Validation evidence: token issuance unit tests and manual email smoke check
  Status: complete
- TASK-004:
  Validation evidence: session-expiry regression test mentioned in review, but not linked in task note
  Status: partial

## Gaps

- Gap ID: GAP-001
  Blocking: No
  Missing link: `TASK-004` needs an explicit validation note tying the regression test to `AC-003`
  Recommended repair: update `tasks.md` validation note and rerun `/spec-review`

## Recommendation

- Next step: repair the missing task-to-validation link before closeout
- Owning artifact or skill: `/spec-implement`
