class CancellationManager:
    def __init__(self):
        self._cancelled = set()

    def cancel_turn(self, turn_id):
        self._cancelled.add(turn_id)

    def is_cancelled(self, turn_id):
        return turn_id in self._cancelled

    def clear(self, turn_id):
        self._cancelled.discard(turn_id)
