"""Smoke coverage for Minh's CLI and the lead's shared entry point."""

import subprocess
import sys
from pathlib import Path

import pytest

BOOTCAMP = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("module", ["members.mikaelvo639.w3.cli", "shared.study_planner"])
def test_cli_runs_real_pipeline_with_reproducible_date(tmp_path: Path, module: str) -> None:
    """Catch entrypoint, date forwarding, prioritisation and allocation errors."""
    csv_path = tmp_path / "tasks.csv"
    csv_path.write_text(
        "title,importance,effort_h,deadline\nDS exam,5,6,2026-10-30\nAssignment,4,1.5,2026-10-27\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-B", "-m", module, str(csv_path), "--hours", "2", "--today", "2026-10-26"],
        cwd=BOOTCAMP,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Tonight (2.0 h):" in result.stdout
    assert result.stdout.index("Assignment") < result.stdout.index("DS exam")
    assert "1.5 h" in result.stdout and "0.5 h" in result.stdout


def test_personal_cli_missing_file_exits_one(tmp_path: Path) -> None:
    """Catch tracebacks or success status for a missing input CSV."""
    missing = tmp_path / "missing.csv"
    result = subprocess.run(
        [sys.executable, "-B", "-m", "members.mikaelvo639.w3.cli", str(missing)],
        cwd=BOOTCAMP,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "not found" in result.stderr.lower() and str(missing) in result.stderr
    assert "Traceback" not in result.stderr


def test_personal_cli_rejects_invalid_today(tmp_path: Path) -> None:
    """Catch invalid date options being ignored before planning."""
    result = subprocess.run(
        [sys.executable, "-B", "-m", "members.mikaelvo639.w3.cli", str(tmp_path / "tasks.csv"), "--today", "bad"],
        cwd=BOOTCAMP,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "--today" in result.stderr


@pytest.mark.parametrize("hours", ["nan", "inf", "-2"])
def test_invalid_budget_is_an_error_not_a_successful_plan(tmp_path: Path, hours: str) -> None:
    """Do not allocate all tasks for NaN or silently accept a negative budget."""
    path = tmp_path / "tasks.csv"
    path.write_text("title,importance,effort_h,deadline\nTask,3,2,2026-10-30\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-B", "-m", "members.mikaelvo639.w3.cli", str(path), "--hours", hours],
        cwd=BOOTCAMP,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 1 and result.stdout == ""
    assert "invalid" in result.stderr.lower() and "Traceback" not in result.stderr
