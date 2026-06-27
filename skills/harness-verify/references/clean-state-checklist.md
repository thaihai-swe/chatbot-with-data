# Clean-State Checklist

Before a feature can pass the gate, the repository must be in a deployable, pristine state.

- [ ] **Tests:** All tests pass across the entire repository (no regressions).
- [ ] **Linting:** Lint is clean (zero warnings, zero errors introduced).
- [ ] **Types:** Type checker passes with zero errors (if applicable).
- [ ] **Build:** The application builds successfully from a clean state.
- [ ] **Git State:** No uncommitted source code changes that affect the feature.
- [ ] **Debt:** No `TODO` or `FIX-ME` items introduced by this feature without corresponding tracking tickets.
- [ ] **Cruft:** No dead code, unused imports, or orphaned files left behind by this feature.
