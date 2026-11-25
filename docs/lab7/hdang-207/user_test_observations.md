# Lab 7 homework — 10-minute usability test

Tester (not in your team, first name only): Huy  Date: 2026-11-24
Task you gave them: "Find out if you can register your thesis with 118 credits, and where to replace a lost student card."

Rule: do not help or explain. Watch and write down what happens.

| # | What the tester did or said | What they expected | Why the system/UI caused it | Fix idea |
|---|---|---|---|---|
| 1 | Clicked 👍 on the thesis answer, saw the toast briefly, then looked confused when the buttons vanished. | Expected a persistent confirmation (e.g., "Feedback recorded") to stay visible under the answer. | `app.py` hid the 👍/👎 buttons once `rid` was added to `st.session_state.rated` without rendering a status caption. | Show `st.caption("✓ Feedback recorded")` when `rid in st.session_state.rated`. |
| 2 | Opened the app on a narrow/phone-width window and typed the first question manually instead of using the sidebar examples. | Expected example questions to be visible on the main screen without opening a menu. | Streamlit collapses `st.sidebar` by default on narrow viewports. | Surface a compact row of example chips or a short hint in the main area on mobile. |
| 3 | Typed "lost student card" and waited, unsure if the assistant was still loading before seeing the answer. | Expected clear progress feedback immediately after pressing Enter. | The spinner appeared, but on a fast/local response or rerun the transition felt abrupt. | Keep `st.spinner("Thinking…")` and ensure the user message renders immediately before the API call. |

The one change we made (commit link): (add commit hash after committing `ui/app.py`)
Before / after screenshot: `docs/lab7/hdang-207/before_fix.png` / `docs/lab7/hdang-207/after_fix.png`
