# AI use log

## 2026-10-24 - Repository preparation

- Tool: OpenAI Codex.
- Request: prepare the Group 04 starter repository using `public_materials/lab03`.
- Assistance: imported the original course files, prepared the package/configuration skeleton,
  wrote deterministic characterisation tests, and drafted setup instructions and the target architecture.
- The original files under `lab03/` were preserved. Refactored modules and an H1 feature were not implemented.
- Student manual review: not recorded. Each member must inspect and verify any material they use.

## 2026-10-24 - Repository cleanup

- Tool: OpenAI Codex.
- Request: use English throughout the repository, remove material outside the lab requirements,
  keep task assignments outside the repository, and leave implementation to the team.
- Assistance: translated repository documentation, consolidated lab instructions in the README,
  removed planning/progress/verification documents, and moved the team assignment outside the repository.
- No refactored service or homework feature was implemented during this cleanup.

## 2026-10-24 - Knowledge module refactoring (Đăng)

- Tool: Antigravity IDE (Gemini 3.8 Flash).
- Request: Refactor office directory and handbook lookup from monolith into `knowledge.py` with OOP classes `OfficeDirectory` and `Handbook`, robust data error handling, and comprehensive unit tests.
- Assistance: Created `OfficeDirectory` and `Handbook` with factory methods `from_csv` and `from_json`, input validation for missing/corrupted files, and 20 unit tests covering happy paths and failure modes.
- Student manual review: Adjusted API methods (`find`, `names`, `search`) to strictly conform to Lab 3 manual specifications, verified seamless integration with `router.py`, and ensured 100% clean Ruff checks and pytest pass.

For H1, add a separate entry with the actual prompt, feature, changed files, and manual review.
These preparation entries do not satisfy the requirement to document three improvements to AI-generated code.

## 2026-10-24 - Light-orange CLI responses (@LePhanDucMan-pa)

- Tool: OpenAI Codex.
- Prompt: add a command-line feature that displays the human-facing service response in
  light orange while leaving the automatically generated JSON log plain white.
- Feature: isolated ANSI styling to answers written to stdout; structured logs on stderr
  remain uncolored and machine-readable.
- Improvements after review: added an explicit reset sequence, disabled color for redirected
  output and `NO_COLOR`, added a `--no-color` option, and covered answer and log behavior with tests.
- Changed files: `src/assistant_core/console.py`, `src/assistant_core/__main__.py`, CLI color tests,
  logging tests, `README.md`, `docs/architecture.md`, and `docs/lab3/ai_extension_review.md`.
- Verification performed by @LePhanDucMan-pa: exercised greeting, tuition, office, handbook,
  unknown-question, and invalid-credit responses in PowerShell; automated suite reached 34 passing tests.
- Manual code review: @LePhanDucMan-pa must confirm understanding of every changed line before submission.

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
