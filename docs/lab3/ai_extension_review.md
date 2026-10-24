# Lab 3 - H1 AI extension review: capability help

**Status:** feature and automated checks implemented; the review below is AI-assisted technical work.
Minh's required manual inspection and confirmation remain pending. These notes do not claim that Minh
personally performed the review or completed the submission.

## Feature-generation prompt

The following feature prompt was prepared and sent by Codex under Minh's request to finish his remaining work:

> Extend the assistant service with a help question that lists what the bot can do.

Additional constraints were to retain OOP and the current service interface, use no network or new dependencies,
and preserve the original monolith. A separate AI subtask generated the first-pass proposal; Codex then reviewed,
tested, and refined it. The draft proposed `Intent.HELP`, complete help aliases with optional greeting prefixes,
and a static capability response including a fixed `12 credits and 2 retakes` example.

## Actual refinements to the generated proposal

| # | Initial AI proposal | Limitation identified | Change made | Evidence and reason |
| --- | --- | --- | --- | --- |
| 1 | Static `_help()` with a fixed 12-credit example | The example exceeds a configured limit smaller than 12 and does not show the configured rate | Made `_help()` an instance method, using `min(12, settings.max_credits)` and the configured rate/limit | A custom 5-credit limit and 500,000 VND rate produce a valid 5-credit example; a real fee request verifies the configuration |
| 2 | Generic office instruction without an available-office example | It is less actionable and does not establish that the suggested lookup exists in the loaded directory | Build an example from the public `offices.names` property, with a safe empty-directory message | A custom Registrar directory is reflected in help and its real lookup succeeds; no hard-coded Library assumption |
| 3 | Help-alias normalization embedded in the main routing function | Extra text normalization obscures intent-priority logic and increases the router's responsibilities | Extracted a focused `_is_help_request()` helper; retained exact alias matching and added domain-collision checks | Case/whitespace/punctuation aliases work, while IT Helpdesk, tuition and thesis questions retain their original domain intents |
| 4 | Suggested tests, without a real process-level verification in the generated diff | Unit-only checks would miss CLI output or logging integration errors | Added real CLI help-question and JSON stderr checks, plus a provider-independence check | `python -m assistant_core help` exits 0; help returns typed metadata, empty sources and `degraded=False` even with an outage-configured responder |

The initial typed `Intent.HELP` and router -> service boundary were retained; they are not claimed as later corrections.
No API call, extra dependency, secret logging, random failure, or new mutable domain global was added.
See `tests/test_help.py` and the H1 entry in `docs/ai-use-log.md`.

## Minh's remaining confirmation

- [ ] Read the initial behavior/refinements and the final models/router/service/tests.
- [ ] Run or inspect the actual test results and confirm understanding of the changes.
- [ ] Add any further changes made personally and accurately identify their author.
- [ ] Obtain the required human review/merge and submit the merged PR link on LMS.
