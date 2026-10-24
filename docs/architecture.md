# Architecture of assistant_core

Status: all ten core modules are implemented on Minh's personal refactor branch.
The branch integrates Thinh's published models/errors/tools/router work and completes the remaining modules
with AI assistance. Real-module integration tests cover the service, CLI, data, configuration, and logging.
No missing-module substitutes are used.

## 1. Module responsibilities

| Module | Responsibility |
| --- | --- |
| `config.py` | Load and validate settings from environment variables and `.env` |
| `errors.py` | Define `AssistantError`, `ConfigError`, `DataError`, `InvalidRequest`, and `ProviderError` |
| `models.py` | Define the public types `Message`, `Response`, `Intent`, and `Source` |
| `router.py` | Select an intent using simple rules |
| `knowledge.py` | Load CSV/JSON data, look up offices, and search handbook rules |
| `tools.py` | Parse credit counts and calculate tuition deterministically |
| `responder.py` | Define the `Responder` protocol, template responder, and provider stub |
| `service.py` | Coordinate the components through one public entry point |
| `logging_setup.py` | Write structured JSON logs to stderr without keys or full user messages |
| `__main__.py` | Provide the CLI and write answers to stdout |

## 2. Service interface

```python
AssistantService.handle(msg: Message) -> Response
```

- `Message`: `text` has 1-2000 characters; `session_id` defaults to `local`.
- `Response`: `answer`, `intent`, `sources: list[Source]`, and `degraded: bool`.
- `Source`: `id` and `title`.
- `Intent`: `greeting`, `fee`, `office`, `rule`, and `unknown`.
- Pydantic rejects invalid input at the boundary with `ValidationError`.
- Missing or invalid configuration/data prevents startup with `ConfigError` or `DataError`.
- A `ProviderError` triggers the template fallback, preserves sources, and sets `degraded=True`.
- An `InvalidRequest` from credit parsing or tuition calculation becomes a fee response with the explanation.
- Unexpected programming errors propagate rather than being hidden as provider failures.

The service emits one `handled` log record for each returned response with `intent`, `latency_ms`,
`session`, and `degraded`. Provider failure adds a generic warning without the exception payload.
The service never logs the full message or settings. JSON formatting and stderr handlers belong to `logging_setup.py`.

## 3. Three design decisions

1. Calculate tuition with pure functions in `tools.py` so results are exact and easy to test.
2. Inject a provider behind the `Responder` protocol so it can be replaced or made to fail in tests
   without changing the service. The stub keeps tests offline and independent of API keys.
3. Read configuration from the environment and document it in `.env.example` so settings can change
   without editing code or committing real keys. The CLI composition root constructs the configured objects;
   the service itself does not load files or read environment variables.

## 4. Collaborator contracts for integration

The design uses object composition rather than a single class containing every capability.
`AssistantService` owns orchestration; its collaborators own configuration, lookup, calculation, and explanation.
The following names and signatures are consumed by the implemented service and CLI:

| Module | Required public contract |
| --- | --- |
| `config` | `load_settings() -> Settings`; settings expose `data_dir: Path`, `llm_provider`, `log_level`, `credit_rate_vnd`, `retake_multiplier`, and `max_credits` |
| `models` | Pydantic `Message`, `Response`, and `Source`; string enum `Intent` with `GREETING`, `FEE`, `OFFICE`, `RULE`, and `UNKNOWN` |
| `errors` | `ConfigError`, `DataError`, `InvalidRequest`, and `ProviderError`, derived from `AssistantError` |
| `knowledge` | `OfficeDirectory.from_csv(path: Path)`, `.names: set[str]`, `.find(text) -> Office or None`; `Office` exposes `name`, `room`, `hours` |
| `knowledge` | `Handbook.from_json(path: Path)`, `.search(query) -> Rule or None`; `Rule` exposes `id`, `title`, `text` |
| `router` | `route(text: str, office_names: set[str]) -> Intent` |
| `tools` | `parse_credits(text: str) -> tuple[int, int]`; `tuition(credits, retake, rate, retake_multiplier, max_credits) -> int` |
| `responder` | `Responder.explain(question: str, rule: Rule) -> str`; no-argument `TemplateResponder()` and `StubLLMResponder()` constructors |
| `logging_setup` | `setup_logging(level: str) -> None`, configuring JSON logs to stderr |

The CLI's `build_service()` loads settings, configures logging, opens the two knowledge files under `data_dir`,
constructs the stub responder, and injects these objects into `AssistantService`.
Only `LLM_PROVIDER=stub` is supported in this lab; another provider raises `ConfigError`.
`TemplateResponder` is the service's fallback and requires no network or key.

`main(argv) -> int` constructs a validated `Message`, calls the service, and prints only the answer to stdout.
It accepts question words and an optional `--session-id` (default `local`). Argument help (`--help`) is available
before application startup. Known startup/validation errors return 2 with a safe stderr message.

`Settings` validates environment variables over optional dotenv values without mutating the process environment.
API keys are excluded from representations and serialization. Invalid settings become a safe `ConfigError`.
`Office` and `Rule` are frozen dataclasses; directory/handbook objects own defensive copies of their records.
CSV/JSON loaders reject missing files, malformed schemas, incomplete records, and duplicate identities with `DataError`.
Search is a deterministic keyword-overlap baseline with input order breaking ties.

## 5. Verification scope

`tests/test_service.py` checks the actual service against controlled collaborators, including configured fees,
office/rule misses, preserved sources, provider fallback, safe metadata, and unexpected-error propagation.
`tests/test_cli.py` checks the actual CLI's composition, input/output, startup errors, and module entry point.
`tests/component_fixtures.py` creates real collaborators with small deterministic records.
`tests/test_integration.py` verifies real course-data flows, a failing real stub, JSON stderr logs,
cross-directory CLI execution, and missing-handbook startup failure.
The original monolith tests remain unchanged. Existing teammate tests remain part of the complete suite.
