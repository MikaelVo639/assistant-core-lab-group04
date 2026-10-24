# AI use log

Entries describe the state when the assistance occurred; the latest entry supersedes earlier pending implementation notes.

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

## 2026-10-24 - Minh's service and CLI contribution

- Tool: OpenAI Codex.
- Request: implement Minh's assigned service, CLI, architecture documentation, and tests using OOP.
- Assistance: implemented `AssistantService` with constructor injection, routing orchestration,
  configured tuition calls, source preservation, named provider fallback, and safe logging metadata.
  Added the CLI composition root and documented the exact collaborator contracts.
- Tests: original monolith characterisation plus service/CLI component tests. Missing collaborator modules
  use test-only contract substitutes; actual modules take precedence once available.
- Scope: other members' modules, full real-module integration, individual H1, and student manual review remain pending.
- Student manual review: not recorded. Minh must read the code and confirm any material used in the submission.

## 2026-10-24 - Minh's remaining individual work

- Tool: OpenAI Codex, with focused AI subtasks for bootcamp code, official-source reading, and read-only contribution audit.
- User request: finish Minh's remaining work, then check published teammate completion.
- Integrated Thinh's merged models/errors/tools/router/CI history without claiming that contribution as Minh's original work.
- Added actual configuration, knowledge loaders, deterministic responders and JSON logging; removed missing-module test substitutes.
- Added real data/CLI/fallback integration checks and regression tests for negative/fractional credits and greeting-prefix routing.
- H1 feature-generation prompt: "Extend the assistant service with a help question that lists what the bot can do."
  The actual first-pass AI proposal was reviewed and refined: configured credit examples, available-office examples,
  and extracted exact help matching with domain-collision and real CLI tests. Details are in `docs/lab3/ai_extension_review.md`.
- Filled the before/after worksheet using AST counts, isolated Ruff checks, and observed behavior; unmeasured human timings are labelled.
- Prepared the H3 technical reflection from five official readings, with a student-review marker.
- W3 bootcamp uses new AI-assisted prerequisite code because no historic W2 implementation was present; it does not establish past W2 activity.
- All implementation and verification work in this entry was AI-assisted. Minh's manual review, personal reading/reflection,
  actual hours, assigned human reviews, merges and submission have not been claimed or recorded as completed.
