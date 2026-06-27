# Traceability Guide

## Purpose

This guide defines how to embed spec traceability markers (`REQ-*`, `AC-*`, `TASK-*`) into source code, tests, and pull request descriptions so that the `/harness-verify` alignment audit can confirm end-to-end traceability from requirements to proof.

## Why Traceability Matters

The alignment audit in `/harness-verify` checks that every `REQ-*` in `spec.md` maps to an `AC-*`, and every `AC-*` maps to a `TASK-*` in `tasks.md`, and every task has a proof command. Embedding these identifiers in the code itself creates a machine-checkable chain: `spec.md → tasks.md → source code → test output`.

Without embedded markers, the audit can only check artifacts — it cannot verify that the right code was written for the right requirement.

## Embedding Conventions

### In Source Code (inline comments)

Place a traceability comment at the implementation site of a requirement:

```python
# AC-001: User must be authenticated before accessing /api/profile
def get_profile(request):
    if not request.user.is_authenticated:
        return Response(status=401)
    ...
```

```typescript
// AC-003: Cart total must include tax at the checkout summary step
function calculateTotal(cart: Cart): number {
    return cart.subtotal + calculateTax(cart);  // AC-003
}
```

```go
// REQ-002 / AC-005: Rate limiter must reject after 100 requests per minute
func (h *Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
```

**Rules:**
- Place the comment on the line before or the same line as the behavior.
- Use the format `// AC-NNN` or `// REQ-NNN` — either is acceptable.
- For multi-line implementations, comment at the entry point (function/method/class) not each line.
- Do not embed `TASK-*` identifiers in production code — tasks are implementation units, not behavior contracts.

### In Test Names and Descriptions

Name tests to reference the acceptance criterion they prove:

```python
def test_ac001_unauthenticated_user_gets_401():
    ...

class TestAC003CartTaxCalculation:
    def test_subtotal_plus_tax_returned():
        ...
```

```typescript
describe("AC-002: checkout enforces minimum order", () => {
    it("rejects orders below $5.00", () => { ... });
});
```

**Rules:**
- Include the `AC-NNN` prefix in the test name, description, or `describe` block.
- If a test covers multiple ACs, list all: `test_ac001_ac002_checkout_flow`.
- Integration and end-to-end tests can reference `REQ-*` when they cover a full requirement rather than one criterion.

### In Pull Request Descriptions

Add a traceability table to the PR description when submitting implementation for review:

```markdown
## Traceability

| Requirement | Acceptance Criterion | Task | Proof |
|---|---|---|---|
| REQ-001 | AC-001, AC-002 | TASK-01 | `pytest test_auth.py -v` exits 0 |
| REQ-002 | AC-003 | TASK-02 | `npm test -- --grep "AC-003"` exits 0 |
```

### In `tasks.md`

The `spec-implement` skill writes proof commands and evidence into each task block. The format in `tasks.md` should cross-reference the AC explicitly:

```markdown
### TASK-01

**Implements:** AC-001, AC-002
**Proof command:** `pytest tests/test_auth.py -v`
**Proof evidence:** All tests pass; exit code 0 recorded at YYYY-MM-DD HH:MM.
**Status:** Done
```

## Alignment Audit Expectations

During `/harness-verify` Alignment Audit, the agent will check:

1. Every `REQ-*` in `spec.md` is covered by at least one `AC-*`.
2. Every `AC-*` maps to at least one `TASK-*` in `tasks.md`.
3. Every `TASK-*` has a proof command and a recorded evidence entry.
4. (Optional for Complex profile) Source code or test files contain `AC-*` comments or test names matching the verified criteria.

If step 4 is performed, the agent uses `grep` to search for `AC-NNN` patterns across `src/`, `tests/`, or equivalent directories. Missing markers do not automatically fail the audit for Moderate profile but are noted as a gap.

## Profile Guidance

| Profile | Traceability Requirement |
|---------|--------------------------|
| Simple | `tasks.md` proof commands only — no inline markers required |
| Moderate | `tasks.md` proof evidence required; inline markers recommended |
| Complex | Inline markers in source + test names + PR table all required; alignment audit checks all three |

## Anti-Patterns

| Anti-Pattern | Why Bad | Fix |
|---|---|---|
| Commenting `# TODO: AC-001` | Marks intent, not completion | Remove TODO; add only when implemented |
| Copying all ACs into every function | Noise that hides real traceability | One comment per implementation site |
| Only marking in tests, not in source | Proof is there but causation is unclear | Mark both test and implementation site |
| Using `# TASK-01` in source code | Tasks are delivery units, not behavioral contracts | Use `AC-*` for behavior; `TASK-*` only in `tasks.md` |
