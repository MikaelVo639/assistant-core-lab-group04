# assistant-core-lab-group04

CSC10014 Lab 03: Engineering a Maintainable Python Service, Group 04.

## Current status

Minh's personal branch contains the full refactored package, the original course materials, working data,
pinned dependencies, a measured before/after worksheet, and real-module tests.
It integrates the models/errors/tools/router work already merged from Thinh's contribution and completes
configuration, knowledge loading, responders, logging, service, and CLI with AI assistance.
H1 adds a deterministic capability-help question. AI-use and review provenance are recorded in the lab documents.
Student manual review, assigned peer approvals, LMS submission, and team completion remain separate requirements.

## Setup

Use Python 3.10 or later. Run these commands from the repository root in Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
```

The environment does not need to be activated when its Python executable is called directly.
`.env.example` documents the configuration settings.
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
src/assistant_core/             Complete refactored package and H1 help feature
tests/                          Characterisation, unit, and real integration tests
docs/architecture.md            Target modules, service interface, and design decisions
docs/ai-use-log.md              Record of AI assistance
docs/lab3/before_after.md        Individual maintainability worksheet
docs/lab3/ai_extension_review.md H1 changes and AI-assisted review provenance
docs/lab3/reflection.md          H3 technical reflection draft for Minh's review
pyproject.toml                  Package, pytest, and Ruff configuration
requirements.txt                Exact dependency versions
.env.example                    Configuration template
```

## Service and CLI

`AssistantService(settings, offices, handbook, responder)` receives its collaborators through the constructor.
Its public entry point is `handle(Message) -> Response`. Domain calculations and data access stay in their
dedicated modules; the service chooses the flow, preserves sources, handles provider fallback, and logs metadata.
The exact collaborator interfaces are listed in `docs/architecture.md`.

Display command-line usage:

```powershell
.\.venv\Scripts\python.exe -m assistant_core --help
```

Run a question or ask for the configured capabilities:

```powershell
.\.venv\Scripts\python.exe -m assistant_core "tuition for 18 credits and 2 retake"
.\.venv\Scripts\python.exe -m assistant_core --session-id demo "where is the library"
.\.venv\Scripts\python.exe -m assistant_core "help"
```

Answers go to stdout. The logging module configures JSON logs on stderr.
The CLI returns 0 for an answer and 2 for invalid input or startup failure, without printing sensitive error values.
Missing or malformed knowledge files prevent startup with a safe error rather than a partial answer.
For W3 bootcamp exercises and the study planner, use the companion `py/w3-mikaelvo639` branch/PR.

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
