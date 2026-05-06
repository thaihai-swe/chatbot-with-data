"""Simple cancellation tracking."""
from __future__ import annotations

from typing import Set

_cancelled_turns: Set[str] = set()

def cancel_turn(turn_id: str):
    _cancelled_turns.add(turn_id)

def is_cancelled(turn_id: str) -> bool:
    return turn_id in _cancelled_turns

def clear_cancellation(turn_id: str):
    if turn_id in _cancelled_turns:
        _cancelled_turns.remove(turn_id)
