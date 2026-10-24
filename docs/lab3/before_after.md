# Lab 3 — Before / after maintainability comparison

AI-assisted technical comparison for Minh's full personal branch. Minh must review and confirm it before submission.
Counts refer to `assistant_core`, not the preserved teaching snapshot or bootcamp code.

| Question | Before | After |
|---|---|---|
| Where would you change the credit rate? How many places? | One source constant, `RATE`, must be edited | One deployment setting, `CREDIT_RATE_VND`, can change without source edits |
| Can you run the tests without internet or an API key? | The script is offline, but its stub sleeps and fails randomly; characterisation tests replace it deterministically | Yes; the real stub is offline, deterministic, and supports an explicit failure switch |
| What happens if `handbook.json` is missing? | Prints an error and continues with an empty handbook, then cannot find rules | Raises `DataError` at startup; CLI exits 2 without an answer |
| Is any secret printed or logged? | The teaching placeholder key is printed by debug code | No key or full question is emitted by the refactored service/CLI; key is excluded from settings repr/serialization |
| How long does it take a new teammate to find the fee logic? | Human timing not measured; fee logic is mixed into `handle()` | Human timing not measured; calculation is named `tools.tuition()` and called by `service._fee()` |
| Number of global variables | 9 module bindings, including `BASE`; 3 mutable domain-data globals | 5 module bindings: 4 immutable routing constants and 1 logger; 0 mutable domain-data globals |
| Number of bare `except:` blocks | 3 | 0 |
| Lines in the longest function | 56, `handle()` | 26, `tools.tuition()` |
| `ruff check` issues | 8 using isolated E/F/I/B/UP/BLE rules, Python 3.10 target and 120 columns | 0 for the configured source/test check; the unchanged teaching monolith is intentionally excluded |
| Can you swap the LLM without touching the service? | No; `handle()` directly calls the module's `llm()` | Yes; inject another `Responder` object through the constructor |

**Three sentences:**
Separating deterministic tools, typed boundaries and injected data/provider objects makes the assistant easier to test and debug.
The trade-off is more files and interfaces to understand than the original script.
The next improvement would be broader retrieval evaluation before replacing the baseline search or adding a real provider.

## Measurement method

AST counts use module-level assignments, `ExceptHandler(type=None)`, and inclusive `end_lineno - lineno + 1`
for functions/methods; imports, class declarations and local variables are not module-assignment counts.
The isolated baseline check uses `ruff check --isolated --target-version py310 --line-length 120 --select E,F,I,B,UP,BLE`.
Runtime checks cover real data, custom configuration, cross-directory CLI execution, and provider failure.
No student reading time or manual review is inferred from automated checks.
