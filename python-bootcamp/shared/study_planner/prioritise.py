"""Rank tasks by the tutorial's importance divided by days-left score."""

from datetime import date

from shared.contract import Task


def prioritise(tasks: list[Task], today: date) -> list[Task]:
    """Return descending scores, using one day for due/overdue tasks.

    Preserve original order for equal scores and leave the input unchanged.
    """
    return sorted(tasks, key=lambda task: task.importance / max(1, task.days_left(today)), reverse=True)
