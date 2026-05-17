# Proposal: 6.1 Descriptive Document Titles

**Status:** Draft
**Date:** 2026-05-17
**Author:** Gemini CLI

## 1. Problem Statement
Currently, when a user uploads a file, the system renames it to a UUID for storage. The document extraction logic uses this UUID-based filename as the document title. This results in documents appearing with cryptic titles like `a1b2c3d4-e5f6-7890-abcd-ef1234567890` in the UI, which is confusing and makes it difficult for users to identify their content.

## 2. Proposed Solution
We will modify the ingestion pipeline to preserve and use the original filename (the `submitted_filename`) as a fallback title when no other descriptive title (like PDF metadata) is found.

### Key Changes:
- **`ExtractorDispatcher`**: Update the `extract` method to accept an optional `fallback_title` parameter.
- **`PdfExtractor` & `TextExtractor`**: Update their `extract` methods to use the `fallback_title` if a title cannot be extracted from the file's internal metadata.
- **`IngestionService`**: When processing an ingestion attempt, pass the `submitted_filename` from the attempt record to the `ExtractorDispatcher`.
- **`Extractors/Common`**: Ensure `title_from_filename` is used correctly with the hint.

## 3. Scope
### In Scope
- File uploads (PDF, TXT, MD).
- Preserving original filename in the `title` field of the document.
- Maintaining preference for internal PDF metadata if available.

### Out of Scope
- Changing how URLs are titled (will continue to use HTML `<title>` or the URL itself).
- Changing how files are stored (they will remain UUID-named for collision avoidance).

## 4. User Impact
Users will see the original name of the file they uploaded (e.g., "Annual Report 2025.pdf") instead of a GUID in the document library and chat citations.

## 5. Verification Plan
- **Automated Tests:** Update existing ingestion tests to verify that the `title` field matches the `submitted_filename`.
- **Manual Verification:** Upload a file and verify its title in the `DocumentLibrary` screen and in chat citations.
- **Regression:** Ensure PDF metadata titles are still preferred when present.
