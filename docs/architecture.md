# Target architecture for assistant_core

Status: target design from the Lab 03 tutorial. The modules below are implemented in the
`tranquyetthang27` individual working copy; the team still has to select and integrate the final
base version.

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

## 3. Three design decisions

1. Calculate tuition with pure functions in `tools.py` so results are exact and easy to test.
2. Inject a provider behind the `Responder` protocol so it can be replaced or made to fail in tests
   without changing the service. The stub keeps tests offline and independent of API keys.
3. Read configuration from the environment and document it in `.env.example` so settings can change
   without editing code or committing real keys.
