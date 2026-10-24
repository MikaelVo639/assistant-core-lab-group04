"""Greedily assign a time budget to an already prioritised task list."""

from math import isfinite

from shared.contract import Block, Task


def allocate(tasks: list[Task], hours: float) -> list[Block]:
    """Fill the budget in order, allowing a partial final task without mutation."""
    if not isfinite(hours) or hours < 0:
        raise ValueError("Study hours must be finite and nonnegative")
    remaining = hours
    blocks: list[Block] = []
    for task in tasks:
        if remaining <= 0:
            break
        assigned = min(task.effort_h, remaining)
        if assigned > 0:
            blocks.append(Block(task=task, hours=assigned))
            remaining -= assigned
    return blocks
