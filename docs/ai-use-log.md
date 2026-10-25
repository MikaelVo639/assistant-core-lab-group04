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

## 2026-10-25 - Individual Lab 3 refactor (@tranquyetthang27)

- Tool: OpenCode (DeepSeek V4.1 Flash).
- Prompt: complete the Lab 3 refactor in this working copy, preserve the monolith's business
  logic, follow `docs/architecture.md`, and finish the `tranquyetthang27` scope.
- Assistance: added environment-backed `config.py`, service orchestration, the CLI entry point,
  the responder factory, request-boundary validation, a named exception hierarchy with stable
  error codes, and offline tests for the models, errors, configuration, responder, and service.
  `responder.py` and `logging_setup.py` follow the versions already merged on `origin/main` so the
  interfaces remain compatible with the team's service integration.
- Verification: 143 tests pass; `ruff check .` and `ruff format --check .` both pass. The CLI was
  exercised for greeting, tuition, office, rule, unknown, `--help`, template provider, and invalid
  configuration paths.
- Student manual review: pending. @tranquyetthang27 must inspect every changed line, explain the
  provider-fallback and configuration behavior, and confirm the verification results before submission.
