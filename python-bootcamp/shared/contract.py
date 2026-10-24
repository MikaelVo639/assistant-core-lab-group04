"""AI-assisted new implementation of the tutorial's shared Task/Block contract."""

from dataclasses import dataclass
from datetime import date
from math import isfinite


@dataclass
class Task:
    """A task with importance 1-5, nonnegative effort and a deadline."""

    title: str
    importance: int
    effort_h: float
    deadline: date

    def __post_init__(self) -> None:
        """Reject importance outside the contract and unusable effort values."""
        if not 1 <= self.importance <= 5:
            raise ValueError("importance must be 1-5")
        if not isfinite(self.effort_h) or self.effort_h < 0:
            raise ValueError("effort_h must be finite and nonnegative")

    def days_left(self, today: date) -> int:
        """Return whole days to the deadline, clamped to zero when overdue."""
        return max(0, (self.deadline - today).days)


@dataclass
class Block:
    """Hours assigned to one task in a study plan."""

    task: Task
    hours: float
