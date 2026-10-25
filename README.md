# assistant-core-lab-group04

CSC10014 Lab 03: Engineering a Maintainable Python Service, Group 04.

## Current status

The repository contains the integrated OOP service, original refactor materials, working data, pinned
dependencies, a measured before/after worksheet, and characterisation, unit and integration tests.
It preserves contributions from Thinh (tools/router/CI), Dang (knowledge), Dat (configuration),
Man (responders/logging), Thang (models/errors) and Minh (service/CLI and integration).
AI assistance and technical review are recorded in `docs/ai-use-log.md`.

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
lab03/                          Original monolith, data, and refactor worksheet
data/                           Working CSV and JSON data for the new package
src/assistant_core/             Complete refactored package
tests/                          Characterisation, unit, and real integration tests
docs/architecture.md            Target modules, service interface, and design decisions
docs/ai-use-log.md              Record of AI assistance
docs/lab3/before_after.md        Individual maintainability worksheet
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

Run a question:

```powershell
.\.venv\Scripts\python.exe -m assistant_core "tuition for 18 credits and 2 retake"
.\.venv\Scripts\python.exe -m assistant_core --session-id demo "where is the library"
```

Answers go to stdout. The logging module configures JSON logs on stderr.
The CLI returns 0 for an answer and 2 for invalid input or startup failure, without printing sensitive error values.
Missing or malformed knowledge files prevent startup with a safe error rather than a partial answer.

`LLM_PROVIDER=stub` selects the deterministic provider; `LLM_PROVIDER=template` selects an offline template.
Neither requires an API key. Unsupported providers fail validation. Configuration uses the first nonblank value
from the process environment, `.env`, then documented defaults, without changing the process environment.
Rule answers include a visible source ID as well as structured source metadata.

## Lab deliverables

Each member completes the refactor on a branch named `refactor/assistant-core-<name>`,
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

The team refactor submission uses the `v0.3-core` tag and is due at 23:59 on the day before Lab 4.
Confirm the calendar date on LMS. Completion tags should only be created after the corresponding work is done.

## Course materials

The original refactor script, its two data files, and the before/after worksheet under `lab03/` are preserved from
[the course repository](https://github.com/CSC10014-at-fit-hcmus/public_materials/tree/f30c605c6ff376ac448ddb00fa82ae36347e29a9/lab03),
commit `f30c605c6ff376ac448ddb00fa82ae36347e29a9`.
The root `data/` files are working copies for the refactored package.
