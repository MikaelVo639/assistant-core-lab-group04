# Lab 3 — Before / after maintainability comparison

Fill in for the monolith (before) and your refactored package (after).

| Question | Before | After |
|---|---|---|
| Where would you change the credit rate? How many places? | Hardcoded in `assistant_monolith.py` line 8 (`RATE = 450000`) | In `.env` or environment variable `CREDIT_RATE_VND` (0 code changes) |
| Can you run the tests without internet or an API key? | No, monolith uses sleep and mock LLM calls inline | Yes, all unit tests run offline and deterministically without keys |
| What happens if `handbook.json` is missing? | Prints error and silently leaves empty list, leading to runtime failures | Raises explicit `DataError` during initialization |
| Is any secret printed or logged? | Yes, `API_KEY` is printed in debug statements | No, secrets are excluded from logs and kept in `.env` |
| How long does it take a new teammate to find the fee logic? | Requires reading through 160+ lines of monolith script | Immediately in `assistant_core/tools.py` |
| Number of global variables | 8 (`API_KEY`, `MODEL`, `RATE`, `RETAKE_RATE`, `DEBUG`, `history`, `offices`, `handbook`) | 0 mutable global variables |
| Number of bare `except:` blocks | 4 bare `except:` blocks | 0 bare `except:` blocks |
| Lines in the longest function | 55 lines (`handle()`) | Under 25 lines |
| `ruff check` issues | 30+ lint/formatting violations | 0 errors (all checks pass) |
| Can you swap the LLM without touching the service? | No, `llm()` is tightly coupled inside the monolith | Yes, provider conforms to `Responder` interface |

**Three sentences:**
Code maintainability and testability improved most by isolating tuition calculations and intent routing into pure, deterministic functions with comprehensive unit tests. Modularizing into separate packages and typed boundaries added slightly more structural ceremony and file navigation compared to a single script. For future improvements, intent classification could be expanded with semantic embeddings or pattern configurations to support more flexible question variations.
