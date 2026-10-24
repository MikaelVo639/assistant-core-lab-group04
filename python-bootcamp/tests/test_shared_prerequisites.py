"""Tests for the newly supplied shared prerequisites, not historic W2 work."""

from datetime import date
from pathlib import Path

import pytest


def test_csv_loads_task_fields_and_clamps_overdue_days(tmp_path: Path) -> None:
    """Catch CSV field conversion and overdue dates leaking negative days."""
    from shared.study_planner.parse import parse_csv

    path = tmp_path / "tasks.csv"
    path.write_text("title,importance,effort_h,deadline\nDS exam,5,6,2026-10-30\n", encoding="utf-8")
    task = parse_csv(path)[0]

    assert (task.title, task.importance, task.effort_h, task.deadline) == ("DS exam", 5, 6.0, date(2026, 10, 30))
    assert task.days_left(date(2026, 10, 26)) == 4
    assert task.days_left(date(2026, 11, 1)) == 0


@pytest.mark.parametrize(
    "row",
    ["Bad,6,1,2026-10-30", "Bad,4,no,2026-10-30", "Bad,4,1,invalid", "Bad,4,-1,2026-10-30"],
)
def test_csv_invalid_row_reports_line_number(tmp_path: Path, row: str) -> None:
    """Catch silent invalid rows and errors without their CSV location."""
    from shared.study_planner.parse import parse_csv

    path = tmp_path / "bad.csv"
    path.write_text(f"title,importance,effort_h,deadline\nOK,1,1,2026-10-30\n{row}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="line 3"):
        parse_csv(path)


def test_prioritise_scores_due_today_overdue_and_tied_tasks_without_mutation() -> None:
    """Catch division by zero, ascending order and unstable equal scores."""
    from shared.contract import Task
    from shared.study_planner.prioritise import prioritise

    today = date(2026, 10, 26)
    tasks = [
        Task("Later", 5, 6.0, date(2026, 10, 30)),
        Task("Today", 4, 1.0, today),
        Task("Overdue", 5, 2.0, date(2026, 10, 25)),
        Task("Tied", 4, 1.0, date(2026, 10, 27)),
    ]
    assert [task.title for task in prioritise(tasks, today)] == ["Overdue", "Today", "Tied", "Later"]
    assert [task.title for task in tasks] == ["Later", "Today", "Overdue", "Tied"]


def test_allocate_takes_partial_final_task_and_render_shows_budget() -> None:
    """Catch over-allocation, skipped partial tasks and invisible allocations."""
    from shared.contract import Task
    from shared.study_planner.allocate import allocate
    from shared.study_planner.render import render

    tasks = [Task("Assignment", 4, 1.5, date(2026, 10, 27)), Task("DS exam", 5, 6.0, date(2026, 10, 30))]
    blocks = allocate(tasks, 2.0)
    assert [(block.task.title, block.hours) for block in blocks] == [("Assignment", 1.5), ("DS exam", 0.5)]
    assert tasks[1].effort_h == 6.0
    text = render(blocks)
    assert "Tonight (2.0 h):" in text
    assert "Assignment" in text and "1.5 h" in text
    assert "DS exam" in text and "0.5 h" in text


def test_allocate_zero_budget_and_no_tasks() -> None:
    """Catch blocks created with zero effort or no available hours."""
    from shared.contract import Task
    from shared.study_planner.allocate import allocate

    assert allocate([], 2.0) == []
    assert allocate([Task("Task", 1, 1.0, date(2026, 10, 30))], 0.0) == []
