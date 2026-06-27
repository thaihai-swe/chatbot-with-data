# Post-Ship Sync (Knowledge Sweep)

Invoked automatically by `harness-verify` when a feature's verdict is `Pass`. The sweep is the self-improving step: every shipped feature must either update the knowledge base or explicitly justify why each file was left alone.

The scope of the sweep is determined by the size and complexity of the change:

- **Extremely Narrow (documentation-only, comment changes, typo fixes):** Sweep only `learned-heuristics.md` if any heuristic was learned. Otherwise, record "no heuristic learned" and stop.
- **Moderate Feature / Core Changes:** Perform a full sweep across every memory file listed in `MASTER_INDEX.md`.

Procedure (Moderate and above):

1. **Read `MASTER_INDEX.md`** to enumerate the current memory file set. If `MASTER_INDEX.md` is missing, recreate it from the kit source by re-running `scripts/install.sh <target> --dry-run` to inspect the default, or manually create a minimal `MASTER_INDEX.md` with `## 1. Context Indexes` and the always-load group (`memories/repo/core-policies.md`).
2. **Read the feature artifacts**: `spec.md`, `plan.md`, `review.md`, `session-extracts.md`, and any `adr-*.md` files under `artifacts/features/<slug>/`.
3. **For each memory file in `MASTER_INDEX.md`**, decide one of:
   - **Update** — apply the diff (route through the matching skill section: constitution, security policy, learned heuristics, PKB, architecture, observability log).
   - **Untouched, with reason** — name the file and give a one-line reason it was not changed (e.g., "no normative rule emerged", "no new architectural boundary", "all candidates already deferred").
   - **Skipped** — (Domain pack files only) if the file's granular load condition (e.g., cross-domain API work for `boundaries.md`) was not met during the feature lifecycle, it can be marked Skipped without a distinct reason.
3a. **Domain Boundary Update** (only if the feature touched a tracked domain):
    - Check whether the feature changed a domain's ownership, integration contract, or invariants by reviewing `spec.md`'s `## Current Context` → `Impacted boundaries`.
    - If yes: open `memories/domain/boundaries.md` (or the relevant named domain pack). Edit the `## Owns`, `## Does Not Own`, `## Integration Contracts`, or `## Invariants` sections directly to reflect the post-feature state. Append one row to `## Change Log` with today's date, the feature slug, and a plain-English summary of what changed.
    - If no: mark the domain files `Untouched: feature did not affect domain boundaries or invariants`.
4. **Heuristic Distillation & Deduplication:** When sweeping `learned-heuristics.md`, analyze the file contents before appending any new candidate. Compare new candidates against existing heuristics. If a candidate overlaps, has identical triggers, or addresses the same codebase boundary, do not add a duplicate rule. Instead, merge the lessons, increment the existing heuristic's `recurrence-count`, and distill the text to keep it concise, active-voice, and evidence-grounded.
5. **Run promotion-threshold check**: for each updated file, compare against the thresholds in `core-policies.md` (lines, distinct subtopics, artifact references). If a file crosses a threshold, add it to the `## Promotion Watchlist` section in `MASTER_INDEX.md` and write a one-paragraph promotion proposal to `artifacts/features/<slug>/promotions.md`. Promotion itself requires user approval — never split a file unprompted.
6. **Write the sweep record** to `artifacts/features/<slug>/session-extracts.md` under a new heading `## Post-Ship Sync — <ISO date>`. The record must list every memory file from `MASTER_INDEX.md` with one of:
   - `Updated: <one-line summary of the change> -> <file>`
   - `Untouched: <one-line reason>`
   - `Skipped: Granular load condition not met`
7. **Verify** before reporting back to `harness-verify`:
   - Every file in `MASTER_INDEX.md` appears exactly once in the sweep record.
   - No file is marked `Updated` without a corresponding diff in the same session.
   - No file is marked `Untouched` without a concrete reason — generic reasons such as "nothing changed" do not count.
   - `Skipped` is strictly reserved for domain files whose intent triggers did not match.
   - Promotion watchlist additions have a corresponding proposal under `artifacts/features/<slug>/promotions.md`.

**Stop Conditions**:

- The verify verdict is not `Pass` — the sweep does not run on failed verifications.
- The session-extracts already contain a sweep record for this feature with the same date — re-running requires user confirmation.
- A required input (`review.md`, `MASTER_INDEX.md`) is missing — repair before sweeping.

**Anti-patterns**:

- "Skipped — no updates needed" without enumerating files. Reject.
- Updating PKB or constitution to capture feature-local context. Route to feature artifacts instead.
- Promoting on the strength of one feature's signal. Heuristics still need repetition.
- Auto-splitting a memory file because it hit a threshold. Threshold breach opens a proposal, not an action.
