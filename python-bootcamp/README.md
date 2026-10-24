# Python bootcamp: Minh's Week 3 work

This folder implements Minh's H2 Week 3 exercises (W3-1 through W3-4) and the
Tech Lead's T-W3 CLI integration from tutorial section 18.7. Minh's GitHub login
is `MikaelVo639`; its importable folder is normalized to lowercase
`members/mikaelvo639/w3`. The tutorial also replaces username hyphens with
underscores; this login contains no hyphens.

## Provenance and scope

These are **AI-assisted new implementations** requiring Minh's review and
understanding. There was no existing bootcamp code in this checkout. The shared
Task/Block model, CSV parser, prioritiser, allocator and renderer were therefore
added as minimal W2-style prerequisites for a runnable Week 3 CLI. They are not
evidence that anyone previously completed W2, obtained contract approvals or
authored the separate W2 team module PRs.

The folder includes the official W3 tests and shared test options from
[course commit f30c605](https://github.com/CSC10014-at-fit-hcmus/public_materials/tree/f30c605c6ff376ac448ddb00fa82ae36347e29a9/python-bootcamp),
alongside additional behavioral tests written for this implementation. Official test functions/fixtures are
retained; only formatting is normalized. The `--member` option selects Minh's directory and `--variant`
is the instructor's W1 option. Only Minh's individual directory is populated.

## Run and check

Use Python 3.10 or later with the repository's pytest and Ruff development tools.
From the repository root in PowerShell:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'python-bootcamp')
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider python-bootcamp/tests --member mikaelvo639
.\.venv\Scripts\python.exe -B -m ruff check --no-cache python-bootcamp
```

For the tutorial's module commands, change into `python-bootcamp` first:

```powershell
Set-Location python-bootcamp
..\.venv\Scripts\python.exe -B -m members.mikaelvo639.w3.cli samples/tasks.csv --hours 2 --today 2026-10-26
..\.venv\Scripts\python.exe -B -m shared.study_planner samples/tasks.csv --hours 2 --today 2026-10-26
```

Both commands use the same argparse interface and shared functions:
`parse_csv -> prioritise -> allocate -> render`. Expected output:

```text
Tonight (2.0 h):
  1. Assignment ...... 1.5 h
  2. DS exam ...... 0.5 h
```

The sample CSV reproduces the tutorial's two task rows. `--today` defaults to
the local current date and `--hours` defaults to `2.0`. A missing file produces
a clear stderr message and exit status 1. Invalid or nonfinite/negative budgets and malformed CSV data
also return 1 without a traceback. Invalid command-line options use
argparse's exit status 2.

## Explicit interpretation choices

- `parse_due` accepts YYYY-MM-DD, `tomorrow`, `in N days` (including zero and
  singular `day`), and English weekday abbreviations/full names. Whitespace and
  case are normalized. A weekday always means a future occurrence; Monday on a
  Monday means seven days later. Unknown text and invalid dates raise ValueError.
- `analyse` returns a Counter for counts and a dictionary for per-route p95.
  P95 uses nearest rank: sort a route's n values and select position
  `ceil(0.95 * n) - 1`. Empty input gives empty counts/p95 and `slowest=None`.
  Ties for slowest choose the alphabetically first route. Latencies are assumed
  finite and nonnegative; units are milliseconds. Input is not mutated.
- Shared priority is descending `importance / max(days_left, 1)`, with overdue
  days clamped to zero and stable input order for equal scores. The denominator
  floor avoids division by zero and is a documented choice where W2 is ambiguous.
- Greedy allocation follows priority order, permits a partial final task and
  leaves tasks unchanged. The displayed total is allocated time. These choices
  reproduce the tutorial's two-hour example; completing every task tonight is
  not required by this allocation policy.
- CSV uses the exact header `title,importance,effort_h,deadline`, UTF-8 with an
  optional BOM, and calendar deadlines. Invalid rows report their CSV line.
  Task importance is 1-5 and effort must be finite and nonnegative.

## Review and submission still required

See `PROGRESS.md` and Minh's W3 README. Minh must inspect the AI-assisted code,
inspect the included instructor test results, and write an authentic personal
reflection. Assigned reviewer comments/approval, issue/PR links, merges, CI
evidence and the required commit history remain pending.

T-W3 member 2's separately authored end-to-end test, member 3's team error
handling and agreed infeasible-plan policy (including InfeasiblePlan reuse),
and member 4's shared README and docs demo remain pending. The included CLI
smoke checks do not claim those teammates' contributions. Team W1/W2 setup and
submission evidence are not established by these files. The lead must wait for
all required member merges and green CI before creating `py-w3-done`; no
completion tag is claimed here.
