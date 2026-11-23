# Lab 7 homework — 10-minute usability test

Tester (not in your team, first name only): ____  Date: ____
Task you gave them: "Find out if you can register your thesis with 118 credits, and where to replace a lost student card."

Rule: do not help or explain. Watch and write down what happens.

| # | What the tester did or said | What they expected | Why the system/UI caused it | Fix idea |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

The one change we made (commit link): [`5a96ccc`](https://github.com/MikaelVo639/assistant-core-lab-group04/commit/5a96ccc) — `fix(ui): persist feedback confirmation and show AI notice on mobile` (disables repeated voting via `on_click`, preserves the feedback toast and persistent `✓ Feedback recorded` confirmation only when `send_feedback` succeeds, and surfaces the AI assistant disclosure on phone-width screens).
Before / after screenshot: [before_fix.png](before_fix.png) / [after_fix.png](after_fix.png)
