# Architecture of assistant_core

Status: all ten core modules are implemented in the integrated team package.
The history retains Thinh's tools/router/CI, Dang's knowledge, Dat's configuration, Man's responders/logging,
Thang's models/errors and Minh's service/CLI and regression fixes. Integration and technical review were AI-assisted.
Real-module integration tests cover the service, CLI, data, configuration, and logging.
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

- `Message`: `text` has 1-2000 characters, is trimmed and cannot be blank; `session_id` defaults to `local`.
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
| `responder` | `Responder.explain(question: str, rule: Rule) -> str`; `TemplateResponder()`, `StubLLMResponder(fail=False)` and `make_responder(settings)` |
| `logging_setup` | `setup_logging(level: str) -> None`, configuring JSON logs to stderr |

The CLI's `build_service()` loads settings and configures logging, then calls the public
`service.build_service(settings=None)` factory to load data and inject the selected responder.
The public factory is also exported from `assistant_core` and does not configure application logging.
`LLM_PROVIDER=stub` selects `StubLLMResponder`; `LLM_PROVIDER=template` selects `TemplateResponder`.
Both work without a network or key. Unsupported providers raise `ConfigError`.
`TemplateResponder` is also the service's fallback. Rule answers include a source ID for CLI callers and
retain structured source metadata for other clients.

`main(argv) -> int` constructs a validated `Message`, calls the service, and prints only the answer to stdout.
It accepts question words and an optional `--session-id` (default `local`). Argument help (`--help`) is available
before application startup. Known startup/validation errors return 2 with a safe stderr message.

Immutable `Settings` validates values from a `ConfigSource` through `SettingsLoader`.
`MappingSource` supports explicit mappings; `EnvSource` overlays nonblank process variables on optional dotenv
values without mutating the environment. Blank process variables preserve populated dotenv values; otherwise
missing/blank fields use defaults. API keys are excluded from representations and serialization.
Invalid settings become a safe `ConfigError` naming variables without echoing their values.
`Office` and `Rule` are frozen dataclasses; directory/handbook objects own defensive copies of their records.
CSV/JSON loaders reject missing files, malformed schemas, incomplete records, and duplicate identities with `DataError`.
Search is a deterministic keyword-overlap baseline with input order breaking ties.
Both rule lookup and the optional `RuleMatch` relevance score use the same punctuation-aware token normalization.
The knowledge module also supports file/directory constructors, defensive record-list properties, and formatted
office/fallback helpers; see `docs/knowledge_integration.md` for those compatible public interfaces.

## 5. Verification scope

`tests/test_service.py` checks full service flows against real data and injected configuration.
`tests/test_service_regressions.py` checks controlled collaborators, including configured fees,
office/rule misses, preserved sources, provider fallback, safe metadata, and unexpected-error propagation.
`tests/test_cli.py` checks the actual CLI's composition, input/output, startup errors, and module entry point.
`tests/component_fixtures.py` creates real collaborators with small deterministic records.
`tests/test_knowledge.py` retains the merged knowledge tests; `tests/test_knowledge_validation.py` preserves
the existing validation checks and merge-regression coverage.
`tests/test_integration.py` verifies real course-data flows, a failing real stub, JSON stderr logs,
cross-directory CLI execution, and missing-handbook startup failure.
The original monolith tests remain unchanged. Existing teammate tests remain part of the complete suite.
Overlapping tests are retained in `test_config_regressions.py` and `test_responder_logging_regressions.py`.
Expectations use the unified presentation: formatted VND totals, terminal punctuation and visible rule source IDs.
