"""T-W3 lead entrypoint, reused by Minh's individual W3 command-line tool."""

import argparse
import sys
from datetime import date
from pathlib import Path

from shared.study_planner.allocate import allocate
from shared.study_planner.parse import parse_csv
from shared.study_planner.prioritise import prioritise
from shared.study_planner.render import render


def main(argv: list[str] | None = None) -> int:
    """Parse CLI options and run parse_csv -> prioritise -> allocate -> render.

    The optional budget defaults to two hours and the date defaults to today.
    Missing input files report a clear message on stderr and return status 1.
    Argparse reports malformed options with status 2.
    """
    parser = argparse.ArgumentParser(description="Plan tonight's study from a task CSV.")
    parser.add_argument("path", type=Path, help="CSV with title,importance,effort_h,deadline")
    parser.add_argument("--hours", type=float, default=2.0, help="available study hours (default: 2)")
    parser.add_argument("--today", type=date.fromisoformat, default=date.today(), metavar="YYYY-MM-DD")
    args = parser.parse_args(argv)
    try:
        tasks = parse_csv(args.path)
        ordered = prioritise(tasks, args.today)
        blocks = allocate(ordered, args.hours)
    except FileNotFoundError:
        print(f"Task file not found: {args.path}", file=sys.stderr)
        return 1
    except (ValueError, OSError):
        print("Cannot plan tasks: invalid CSV data or study-hour budget.", file=sys.stderr)
        return 1
    print(render(blocks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
