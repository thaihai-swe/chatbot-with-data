# Handoff: 9.0 Citation Upgrade

## Current State
- **Phase**: Done
- **Status**: Verification passed. Feature fully complete and closed.
- **Verification Result**: Pass (`review.md` generated, all mechanical and alignment gates passed).

## Summary of Completed Work
* **Backend Prompts & Citations**: Prompts are updated to enforce bracket citations; regular expression updated to parse both legacy `[Source N]` and new `[N]` syntax.
* **X-Ray Persistence**: Resolved issue where Pipeline X-Ray metrics (Grounded, Risk, Intent) returned `N/A` on page reload/history load by serializing traces directly into the database's `context_used_json` column.
* **UI/UX Upgrades**:
  * Removed max-width limits globally to make all pages (library, collections, chat, evaluation, settings) span 100% width on desktop.
  * Reverted citation badge clicks to open the popup modal (`CitationModal`).
  * Upgraded inline `SourceBrowser` to render 100% width and display chunk contents in a centered popup modal (`ChunkModal`) with inline note editor.
  * Solved label clipping on collapsed toggles by rotating labels vertically using `writing-mode: vertical-rl`.

## Persistent Memories Sync
* Triaged session extracts and proposed promotions (`promotions.md` created due to `learned-heuristics.md` exceeding 100 lines).
* Logged a `size-warning` to `harness-telemetry.md`.
* Compacted `learned-heuristics.md` successfully, reducing it from 134 to 82 lines (~38.8% reduction) with 100% identifier preservation.

## Next Step / Next Command
None (Feature is fully shipped and closed).
