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
