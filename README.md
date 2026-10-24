# assistant-core-lab-group04

Group 04 starter repository for CSC10014 Lab 03: Engineering a Maintainable Python Service.

## Current status

The repository contains the original course materials, the package skeleton, working data,
pinned dependencies, worksheet templates, and 9 deterministic characterisation tests of the monolith.
The refactored modules and CLI are left for the team to implement.
Passing the current tests does not mean that the refactored package is complete.

## Setup

Use Python 3.10 or later. Run these commands from the repository root in Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
```

The environment does not need to be activated when its Python executable is called directly.
`.env.example` documents the settings for the configuration module to be implemented.
The original monolith does not read these environment variables.
Keep `.env` and real API keys out of Git.

## Run the original script and checks

```powershell
.\.venv\Scripts\python.exe lab03\monolith\assistant_monolith.py --test
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
```

The original demo includes a deliberately unreliable provider stub.
The characterisation tests replace that provider when needed so they run deterministically and offline.
Ruff excludes the original teaching monolith; it checks the new package and tests.

## Repository layout

```text
lab03/                          Original monolith, data, and worksheet templates
data/                           Working CSV and JSON data for the new package
src/assistant_core/             Package skeleton; implementation pending
tests/                          Characterisation tests of the monolith
docs/architecture.md            Target modules, service interface, and design decisions
docs/ai-use-log.md              Record of AI assistance
docs/lab3/before_after.md        Individual maintainability worksheet
docs/lab3/ai_extension_review.md Individual AI-extension review template
pyproject.toml                  Package, pytest, and Ruff configuration
requirements.txt                Exact dependency versions
.env.example                    Configuration template
```

## Lab deliverables

Each member completes the full refactor on a branch named `refactor/assistant-core-<name>`,
runs tests after each step, fills in `docs/lab3/before_after.md`, and opens a PR.
Submit the individual PR link on LMS at the end of the session; a draft PR is accepted.

The team reviews the individual PRs, selects one version as the base, and integrates improvements
with appropriate contributor credit. The final package must include:

- The modules and public interface documented in `docs/architecture.md`.
- Environment-based configuration, typed models, named exceptions, and a tested provider fallback.
- Greeting, tuition, office lookup, and rule search with source information.
- Structured logs without API keys or full user messages.
- At least 10 passing tests, including characterisation tests and tests of the refactored package.
- Clean Ruff checks and formatting, pinned dependencies, and an architecture note with three decisions.

For H1, each member adds an AI-assisted feature, manually improves at least three aspects of its code,
documents the changes in `docs/lab3/ai_extension_review.md`, records AI use, and submits a merged PR link.
For H2, complete W3-1 through W3-4 and the T-W3 team integration of `study_planner`.
For H3, complete the assigned reading and reflection.

The team submission (`v0.3-core`), H1, and H2 (`py-w3-done`) are due at 23:59 on the day before Lab 4.
Confirm the calendar date on LMS. Completion tags should only be created after the corresponding work is done.

## Course materials

The five original files under `lab03/` are preserved unchanged from
[the course repository](https://github.com/CSC10014-at-fit-hcmus/public_materials/tree/f30c605c6ff376ac448ddb00fa82ae36347e29a9/lab03),
commit `f30c605c6ff376ac448ddb00fa82ae36347e29a9`.
The root `data/` files are working copies for the refactored package.
