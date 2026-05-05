export const STATUS_COPY = {
  submitted: {
    label: "Submitted",
    tone: "muted",
    description: "The source was accepted and is waiting to be processed.",
  },
  processing: {
    label: "Processing",
    tone: "info",
    description: "The source is being parsed and checked for duplicates.",
  },
  completed: {
    label: "Completed",
    tone: "success",
    description: "Ingestion finished. The source is stored, but it is not indexed yet.",
  },
  failed: {
    label: "Failed",
    tone: "danger",
    description: "The source could not be processed. Review the error details.",
  },
  skipped: {
    label: "Skipped",
    tone: "warning",
    description: "Ingestion was intentionally skipped after a duplicate decision.",
  },
  awaiting_user_action: {
    label: "Awaiting your choice",
    tone: "warning",
    description: "A duplicate warning needs a decision before the source can continue.",
  },
};

export const DUPLICATE_ACTIONS = [
  { value: "skip_ingestion", label: "Skip ingestion" },
  { value: "replace_existing", label: "Replace existing" },
  { value: "ingest_as_new_version", label: "Ingest as new version" },
  { value: "ingest_anyway", label: "Ingest anyway" },
  { value: "merge_metadata", label: "Merge metadata" },
  { value: "warn_and_continue", label: "Warn and continue" },
];
