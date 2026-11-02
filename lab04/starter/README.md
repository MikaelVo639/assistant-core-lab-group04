# Study Assistant — Lab 4 in-class API

P1–P5 and T1–T4 are implemented. Homework and bonus tasks are excluded.
The starter is standalone with its supplied `assistant_core`; use a separate
environment from the root Lab 3 package to avoid importing the wrong copy.

## Windows PowerShell (from repository root)

```powershell
python -m venv lab04/starter/.venv
lab04/starter/.venv/Scripts/python.exe -m pip install -r lab04/starter/requirements.txt
lab04/starter/.venv/Scripts/python.exe -m pip install -e lab04/starter
cd lab04/starter
.venv/Scripts/python.exe -m pytest -q ../practice
.venv/Scripts/python.exe -m pytest -q tests
Copy-Item .env.example .env
.venv/Scripts/python.exe -m uvicorn assistant_api.main:create_app --factory --reload
```

Use `/docs` to try the endpoints. The example admin key is for local practice only;
keep real keys in the ignored `.env` file. Feedback resets when the server restarts.
Rate limiting remains optional and its test stays skipped.
See [verification evidence](../../docs/lab4/README.md).

## Setup
```
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt && pip install -e .
cp .env.example .env
```
## Run the API
```
uvicorn assistant_api.main:create_app --factory --reload
```
Open http://127.0.0.1:8000/docs for the interactive OpenAPI documentation.

## API contract (v1)
| Method | Path | Body | Success | Errors |
|---|---|---|---|---|
| GET | `/health` | — | 200 `{"status":"ok","version":...}` | — |
| POST | `/v1/chat` | `{"message": str 1–2000, "session_id": str}` | 200 `{answer, intent, sources[], degraded, request_id}` | 422 invalid, 429 rate limit |
| POST | `/v1/feedback` | `{"request_id": str, "rating": -1/0/1, "comment"?: str ≤500}` | 201 feedback with `id`, `created_at` | 422 |
| GET | `/v1/feedback` | header `X-API-Key` | 200 list | 401 |
| GET | `/v1/weather` | — | 200 `{temperature_c, wind_kmh, description, observed_at, stale}` | 503 upstream down |

All errors use one shape: `{"error": {"code": "...", "message": "..."}}`.

## Tests
```
pytest -q                          # unit + API tests (external API mocked)
bash api-tests/curl_tests.sh       # manual tests against a running server
```
Postman / Bruno: import `api-tests/study-assistant.postman_collection.json`.
