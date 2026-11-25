# assistant-core-lab-group04

Lab 4 in-class API: [setup](lab04/starter/README.md) and
[verification evidence](docs/lab4/README.md).
Lab 5 database: [setup](lab05/starter/README.md) and
[verification evidence](docs/lab5/README.md).

CSC10014 Lab 03: Engineering a Maintainable Python Service, Group 04.

## Current status

The repository contains the integrated OOP service, original refactor materials, working data, pinned
dependencies, a measured before/after worksheet, and characterisation, unit and integration tests,
plus Lab 7 Streamlit UI materials (`lab07/`) and usability/reflection records (`docs/lab7/`).
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

## Run the HTTP API (Lab 04)

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m uvicorn assistant_api.main:create_app --factory --reload
```

Open http://127.0.0.1:8000/docs for the OpenAPI documentation. `src/assistant_api/` wraps `AssistantService`
over HTTP; its settings (`API_ADMIN_KEY`, `WEATHER_*`, `CAMPUS_*`, `RATE_LIMIT_PER_MIN`) live in `.env.example`.

| Method | Path | Success | Errors |
|---|---|---|---|
| GET | `/health` | 200 `{"status":"ok","version":...}` | — |
| POST | `/v1/chat` | 200 `{answer, intent, sources[], degraded, request_id}` | 422 invalid, 429 rate limit |
| POST | `/v1/feedback` | 201 feedback with `id`, `created_at` | 422 |
| GET | `/v1/feedback` (header `X-API-Key`) | 200 list | 401 |
| GET | `/v1/weather` | 200 `{temperature_c, wind_kmh, description, observed_at, stale}` | 503 upstream down |

All errors share one shape: `{"error": {"code": "...", "message": "..."}}`. `tests/test_api.py` mocks the weather
upstream; `lab04/starter/api-tests/` has curl and Postman checks for a running server.

## Run the UI (Lab 07)

Run both servers from `lab07\starter` in two separate Windows PowerShell terminals:

**Terminal 1 — Backend API (port 8000):**

```powershell
cd lab07\starter
..\..\.venv\Scripts\python.exe -m uvicorn assistant_api.main:create_app --factory --reload
```

**Terminal 2 — Streamlit UI (port 8501):**

```powershell
cd lab07\starter
..\..\.venv\Scripts\python.exe -m streamlit run ui/app.py
```

Open `http://localhost:8501` in your browser. If the API runs on a different host or port, set `ASSISTANT_API_URL` before starting Streamlit:

```powershell
$env:ASSISTANT_API_URL = "http://127.0.0.1:8001"
..\..\.venv\Scripts\python.exe -m streamlit run ui/app.py
```

### Troubleshooting (Lab 07)

- **Backend not reachable**: Make sure Terminal 1 (`uvicorn`) is running and `http://127.0.0.1:8000/health` returns `{"status":"ok",...}`. If port `8000` is occupied, start `uvicorn` with `--port 8001` and set `$env:ASSISTANT_API_URL = "http://127.0.0.1:8001"` in Terminal 2.
- **`ModuleNotFoundError: No module named 'ui'`**: Run `streamlit run ui/app.py` from `lab07\starter` (not from the repository root or `lab07\starter\ui`).
- **`streamlit: command not found`**: Invoke Streamlit as a Python module using the virtual environment: `..\..\.venv\Scripts\python.exe -m streamlit run ui/app.py`.

## Repository layout

```text
lab03/                          Original monolith, data, and refactor worksheet
data/                           Working CSV and JSON data for the new package
src/assistant_core/             Complete refactored package
src/assistant_api/              FastAPI backend over the service (Lab 04)
lab04/                          Lab 04 starter, practice and worksheets
lab07/                          Lab 07 Streamlit practice, starter UI, and worksheets
tests/                          Characterisation, unit, and real integration tests
docs/architecture.md            Target modules, service interface, and design decisions
docs/ai-use-log.md              Record of AI assistance
docs/lab3/before_after.md        Individual maintainability worksheet
docs/lab7/                      Lab 7 usability checklists, observations, and reflections
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
