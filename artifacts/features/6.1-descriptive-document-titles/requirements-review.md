# Requirements Review: 6.1 Descriptive Document Titles

## Metadata

- Feature name: Descriptive Document Titles
- Feature slug: 6.1-descriptive-document-titles
- Related spec: artifacts/features/6.1-descriptive-document-titles/spec.md
- Reviewer: Gemini CLI
- Status: Completed
- Last updated: 2026-05-17

## Review Summary

- Verdict: ready
- Short summary: The specification clearly defines the problem of GUID-based titles and provides a concrete, testable solution by passing the original filename through the extraction layer.

## Readiness Assessment

- Strengths: Clear fallback logic defined (Metadata > Submitted Filename > UUID). Explicitly preserves UUID-based storage for stability while fixing the user-facing title.
- Main concerns: None.

## Traceability Check

- Requirements covered clearly: Yes
- Acceptance criteria testable: Yes
- Validation method named per acceptance criterion: Yes
- Plan-readiness traceability present: Yes
- Scope boundaries explicit: Yes
- Non-goals explicit: Yes
- Risks and open questions visible: Yes

## Blocking Issues

None.

## Non-Blocking Improvements

- NR-001: The specification could explicitly mention if we should strip file extensions from the title (e.g., "Manual" instead of "Manual.pdf").
  Improvement: The `title_from_filename` helper already uses `.stem`, so extensions will be stripped by default.
  Why it helps: Ensures a cleaner UI.

## Brownfield Observations

- Current context quality: High. Identified exactly where the UUID renaming happens and how it propagates to extractors.
- Unchanged behavior captured: Yes (storage filenames, URL title logic).
- Integration boundaries captured: Yes (IngestionService -> Dispatcher -> Extractors).
- Regression concerns visible: Yes (preference for PDF metadata is maintained).

## Questions To Resolve

None.

## Recommendation

- Next step: Lock the spec and move to planning.
