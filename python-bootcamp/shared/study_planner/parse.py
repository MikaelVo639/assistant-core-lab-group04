"""Load the tutorial's four-column task CSV into the shared contract."""

import csv
from datetime import date
from pathlib import Path

from shared.contract import Task


def parse_csv(path: str | Path) -> list[Task]:
    """Read title,importance,effort_h,deadline; report invalid CSV line numbers.

    Deadlines use YYYY-MM-DD. File-system errors propagate to the caller.
    """
    with open(path, newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["title", "importance", "effort_h", "deadline"]:
            raise ValueError("line 1: expected header title,importance,effort_h,deadline")
        tasks: list[Task] = []
        for row in reader:
            try:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError("expected exactly four fields")
                tasks.append(
                    Task(
                        title=row["title"],
                        importance=int(row["importance"]),
                        effort_h=float(row["effort_h"]),
                        deadline=date.fromisoformat(row["deadline"]),
                    )
                )
            except ValueError as error:
                raise ValueError(f"line {reader.line_num}: {error}") from error
        return tasks
