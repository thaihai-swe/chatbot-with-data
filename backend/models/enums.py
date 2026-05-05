from __future__ import annotations

from enum import Enum


class SourceType(str, Enum):
    PDF = "pdf"
    TEXT = "txt"
    MARKDOWN = "md"
    URL = "url"


class IngestionStatus(str, Enum):
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    AWAITING_USER_ACTION = "awaiting_user_action"


class DuplicateStatus(str, Enum):
    UNIQUE = "unique"
    EXACT_DUPLICATE = "exact_duplicate"
    NEAR_DUPLICATE = "near_duplicate"
    SAME_URL = "same_url"
    SAME_TITLE_DIFFERENT_CONTENT = "same_title_different_content"
    SAME_CONTENT_DIFFERENT_SOURCE = "same_content_different_source"


class DuplicateAction(str, Enum):
    SKIP_INGESTION = "skip_ingestion"
    REPLACE_EXISTING = "replace_existing"
    INGEST_AS_NEW_VERSION = "ingest_as_new_version"
    INGEST_ANYWAY = "ingest_anyway"
    MERGE_METADATA = "merge_metadata"
    WARN_AND_CONTINUE = "warn_and_continue"
