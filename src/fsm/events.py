from dataclasses import dataclass


@dataclass(frozen=True)
class RequestExit:
    """Emitted by StateManager when the OUTRO animation completes."""
