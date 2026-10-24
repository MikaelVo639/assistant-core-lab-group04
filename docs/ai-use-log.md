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

For H1, add a separate entry with the actual prompt, feature, changed files, and manual review.
These preparation entries do not satisfy the requirement to document three improvements to AI-generated code.
