# Lab 4 — API contract worksheet

Fill in one row per endpoint **before** you code it.

| Method | Path | Request body / params | Success (code + body) | Errors (code + error.code) | Who calls it |
|---|---|---|---|---|---|
| GET | /health | — | 200 `{"status": "ok", "version": "1.0.0"}` | — | ops, UI |
| POST | /v1/chat | `{"message": str, "session_id": str}` | 200 `{"answer": str, "intent": str, "sources": list, "degraded": bool, "request_id": str}` | 422 `invalid_request`, 429 `rate_limit_exceeded` | UI, tests |
| POST | /v1/feedback | `{"request_id": str, "rating": int, "comment"?: str}` | 201 `{"id": int, "request_id": str, "rating": int, "comment": str, "created_at": str}` | 422 `invalid_request` | UI |
| GET | /v1/feedback | header `X-API-Key: str` | 200 `[FeedbackOut, ...]` | 401 `missing_or_invalid_api_key` | staff dashboard |
| GET | /v1/weather | — | 200 `{"temperature_c": float, "wind_kmh": float, "description": str, "observed_at": str, "stale": bool}` | 503 `weather_service_unavailable` | UI |
| GET | /v1/offices | — | 200 `[{"name": str, "room": str, "hours": str}, ...]` | — | UI, tests |

Questions:
1. Which fields are required, and what are their limits?
   - `POST /v1/chat`: `message` is required, non-empty, 1–2000 characters. `session_id` is optional string.
   - `POST /v1/feedback`: `request_id` is required. `rating` is required and restricted to -1, 0, or 1. `comment` is optional, max 500 characters.
   - `GET /v1/feedback`: `X-API-Key` header is required and must match configured `ADMIN_API_KEY`.
2. What does the UI show for each error code?
   - `422 (invalid_request)`: Inline form validation message pointing to the invalid input field.
   - `429 (rate_limit_exceeded)`: Temporary throttle warning banner asking user to wait before sending more queries.
   - `401 (missing_or_invalid_api_key)`: Access denied modal or login screen for administrators.
   - `503 (weather_service_unavailable)`: Weather widget status indicator showing service temporarily down or displaying cached fallback data.
3. What changes would force a `/v2`?
   - Breaking API changes, such as renaming existing request/response fields (`message` -> `text`, `answer` -> `response`), changing data types (e.g. integer rating to enum string), altering the error envelope schema, or removing endpoints.
