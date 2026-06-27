# Hallucination Checks

<!-- Used by /harness-maintain Eval Mode to detect fabricated claims in agent output. Apply these patterns when reviewing implementation claims, test results, or verification evidence. -->

## Purpose

AI agents can fabricate file paths, test results, API names, commit hashes, and verification evidence. These checks provide mechanical patterns for detecting hallucinated claims before they corrupt the artifact chain.

## Detection Patterns

### 1. File Path Claims

**Risk:** Agent claims to have created or modified a file that doesn't exist.

**Check:**
- For every file path mentioned in `tasks.md` evidence: verify the file exists
- For every "created file" claim: `ls` the path
- For every import statement in new code: verify the imported module exists

**Red flags:**
- Path uses a naming convention inconsistent with the project
- Path references a directory that doesn't exist
- File extension doesn't match the language being used

### 2. Test Result Claims

**Risk:** Agent claims tests pass without actually running them.

**Check:**
- Evidence must include the exact command run and its output
- Timestamp of test run must be from the current session
- Test count must match the actual test files
- "All tests pass" without naming specific tests is suspicious

**Red flags:**
- Round numbers ("100 tests pass") without specifics
- No command output shown
- Claims of passing tests for code that was just written (no time to run)
- Test names that don't match the testing framework's conventions

### 3. API & Library Claims

**Risk:** Agent references functions, methods, or APIs that don't exist.

**Check:**
- Verify imported functions exist in the dependency
- Check that API endpoints referenced actually exist
- Verify method signatures match the library version in use

**Red flags:**
- Function names that sound plausible but aren't in the docs
- API endpoints with inconsistent URL patterns
- Method signatures that mix conventions from different libraries

### 4. Verification Evidence Claims

**Risk:** Agent claims verification passed based on plausible reasoning rather than actual execution.

**Check:**
- Evidence must include raw command output, not just "it passed"
- Mechanical gate commands must show exit code 0
- Lint/typecheck output must be empty (no errors)
- If evidence says "no changes needed" — verify the diff is actually empty

**Red flags:**
- "I verified this works" without showing how
- Evidence that's too clean (real test output has noise)
- Claims that skip the mechanical gate ("tests are unnecessary for this change")

### 5. Commit & Git Claims

**Risk:** Agent references commits, branches, or git state that doesn't match reality.

**Check:**
- Verify commit hashes with `git log`
- Verify branch existence with `git branch`
- Verify file state matches what the agent claims

**Red flags:**
- Commit hashes that are too short or don't resolve
- Claims about "the last commit" without verifying
- Branch names that don't follow project conventions

## Severity Classification

| Severity | Impact | Action |
|----------|--------|--------|
| Critical | Fabricated verification evidence | Reject the entire verification pass |
| High | Fabricated file paths or test results | Rerun verification from scratch |
| Medium | Incorrect API references | Fix and re-verify affected code |
| Low | Minor naming inconsistencies | Note and correct |

## Application

Apply these checks:
1. During `/harness-verify` Mechanical Gate Audit — verify all evidence is real
2. During `/harness-maintain` Eval Mode — audit agent output quality
3. When reviewing handoff artifacts — verify claims before resuming work
4. After any agent session that produced "too clean" results

## Prevention

The harness prevents hallucination through:
- **Mechanical gates:** Commands must actually run and exit 0
- **Evidence freshness:** Stale evidence is a finding
- **Artifact-first:** If it's not in the artifact with proof, it didn't happen
- **Task discipline:** Proving command named BEFORE editing, run AFTER
