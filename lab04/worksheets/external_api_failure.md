# Lab 4 homework — design for an external service that goes down

Service chosen (weather / maps / news / other approved): Open-Meteo Weather API  Base URL: https://api.open-meteo.com/v1/forecast

| Failure | How you simulate it | What your API returns | What the user sees |
|---|---|---|---|
| timeout | transport raises ConnectTimeout | HTTP 503 `{"error": {"code": "weather_service_unavailable", "message": "Weather service unavailable"}}` (or stale cache if available) | Warning notification indicating weather info is temporarily unreachable, or displays last known temperature with a stale indicator |
| 500 from upstream | MockTransport returns 500 | HTTP 503 `{"error": {"code": "weather_service_unavailable", "message": "Weather service unavailable"}}` (or stale cache if available) | Status banner informing that the external weather provider is down |
| malformed JSON | MockTransport returns `{}` or unexpected structure | HTTP 503 `{"error": {"code": "weather_service_unavailable", "message": "Weather service unavailable"}}` | Fallback message stating current weather data cannot be parsed |
| rate limited (429) | MockTransport returns 429 | HTTP 503 `{"error": {"code": "weather_service_unavailable", "message": "Weather service unavailable"}}` | Temporary advisory that weather updates will resume shortly |

Timeout value and why: 2.0s to ensure chat assistant responsiveness without blocking client threads.  Retries and why: 1 retry with exponential backoff to handle transient network hiccups without overwhelming the upstream service.  Cache TTL and why: 600s (10 min) because weather conditions change slowly and caching avoids redundant remote calls.
Tests added (file + names): `tests/test_api.py` and `lab04/starter/tests/test_api.py` (`test_weather_down_returns_503`, `test_weather_stale_cache_when_upstream_fails`)
