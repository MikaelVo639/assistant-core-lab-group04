# AI use log

## 2026-10-24 - Refactor assistance

- Tool: OpenAI Codex.
- Scope: the Lab 03 maintainable-service refactor, its tests, architecture and before/after worksheet.
- Imported the original refactor script and data, prepared the package, and retained deterministic characterisation tests.
- Integrated Thinh source history for models, errors, tools, router and CI without claiming it as original Minh work.
- Implemented OOP service orchestration, CLI composition, validated configuration, knowledge loading, deterministic responders and JSON logging.
- Added real-module tests and fixes for invalid credit counts, numeric overflow, malformed settings, safe errors and test isolation.
- The before/after worksheet uses measured AST/Ruff results; human reading times are explicitly unmeasured.
- Planning, assignments and contribution audits are stored outside this repository.
- Code and technical review were AI-assisted. Student manual inspection and human PR approvals have not been claimed as completed.

## 2026-10-24 - Update PR #1 from main

- Integrated Dang's merged PR #3 and retained its public knowledge interfaces and original tests.
- Kept the previous validation suite separately and added regressions for duplicate records, unreadable encoding,
  consistent punctuation-aware search scores, constructor keyword compatibility and reordered CSV columns.
- Retained the refactor-only scope and consolidated integration documentation without team task assignments.

## 2026-10-25 - Configuration review and final integration

- Tool: OpenAI Codex, including a separate AI code reviewer.
- Request: fix PR #1, review Dat's PR #6, correct the remaining refactor issues and merge the final team version.
- Reviewed PR #6 for validation, source precedence, API compatibility, secret-safe errors and environment nonmutation.
- Reproduced blank process variables discarding populated dotenv values in two failing tests, fixed the source
  overlay, then verified 156 tests and Ruff before the SHA-guarded merge of PR #6.
- Integrated Dat's immutable settings/source factory, Man's responders/logging, Thang's models/errors and
  Dang's knowledge API while retaining Minh's orchestration and numeric/search/CLI regressions.
- Preserved the existing suites in separate regression files. Updated test setup to construct new immutable
  settings and aligned presentation assertions with one response format; no failing behavior checks were removed.
- Restored contribution provenance from merged PR history and consolidated English refactor documentation.
- Review and integration checks are AI-assisted. They do not establish student understanding or individual
  LMS submission; students must verify their own submissions and any pending manual-review statements.

## Contribution provenance retained from PR history

- Thinh's PR #2 contributed tools, routing, CI and the initial shared models/errors.
- Dang's PR #3 contributed the knowledge implementation, public helpers and its original 20 tests.
  Its AI-use entry records Antigravity assistance and author-reported API/manual adjustments.
- Dat's PR #6 contributed immutable configuration, configuration sources and the settings loader.
- Thang's PR #8 contributed model validation, documented named errors, service composition and tests.
  Its AI-use entry records OpenCode assistance and leaves student manual inspection pending.
- Minh's PR #1 contributed the integration, service/CLI, validation and regression fixes documented above.
- Man's responder/logging AI-use entry from PR #7 is restored below after being omitted in a later merge.

## 2026-10-25 - Responder and structured logging (@LePhanDucMan-pa)

- Tool: OpenAI Codex.
- Request: implement the assigned responder and logging modules after merging the latest `main`, following
  the Lab 03 and Git/GitHub tutorials and the repository's existing public contracts.
- Assistance: implemented the `Responder.explain()` protocol, deterministic template and stub responders,
  simulated `ProviderError`, application-scoped JSON logging to stderr, and focused unit tests.
- Privacy review: logs allow only intent, latency, session, and degraded metadata in addition to the standard
  level, logger, and event message; tests verify that unapproved question and API-key metadata is omitted.
- Integration review: retained the merged `knowledge.Rule` and `ProviderError` types, avoided edits to modules
  owned by teammates, and used the interface expected by the service integration guide.
- Verification: 75 tests passed; `ruff check .` and `ruff format --check .` both passed.
- Student manual review: @LePhanDucMan-pa must inspect the implementation, explain the fallback and logging
  behavior, and confirm all verification results before submission.
