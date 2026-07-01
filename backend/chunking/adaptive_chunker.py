from __future__ import annotations

from chunking.base import BaseChunker


class AdaptiveChunker:
    """Decides whether to inject a document whole (Tier 1) or chunk it (Tier 2).

    Threshold computation:
      1. If ``adaptive_tiering_threshold`` is set (>0), use it directly.
      2. Otherwise: ``max(1000, context_window_size * adaptive_tiering_ratio)``
    """

    def __init__(
        self,
        *,
        threshold: int | None = None,
        enabled: bool = True,
    ) -> None:
        self.enabled = enabled
        self._threshold = threshold if (threshold is not None and threshold > 0) else None

    @property
    def threshold(self) -> int | None:
        return self._threshold

    @classmethod
    def from_config(cls, config) -> AdaptiveChunker:
        enabled = config.ingestion.adaptive_tiering_enabled
        explicit = config.ingestion.adaptive_tiering_threshold
        if explicit is not None and explicit > 0:
            threshold = explicit
        else:
            ratio = config.ingestion.adaptive_tiering_ratio
            window = config.llm.context_window_size
            threshold = max(1000, int(window * ratio))
        return cls(threshold=threshold, enabled=enabled)

    def should_inject(self, text: str) -> bool:
        if not self.enabled:
            return False
        if self._threshold is None:
            return False
        token_count = BaseChunker.estimate_tokens(text)
        return token_count < self._threshold
