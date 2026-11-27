# Lab 7 — Usability checklist — LePhanDucMan-pa

Checked with Codex on 2026-11-27 using the local Streamlit UI and API. These are browser verification results, not an outside-team user test.

- [x] The first screen says what the assistant can do, with example questions
- [ ] Empty or too-long input shows a friendly message (not a crash)
- [x] While waiting, the user sees "Thinking…"
- [x] Every answer from documents shows its sources
- [x] "I don't know" answers tell the user who can help (escalation)
- [x] If the backend is down, the page says so clearly
- [x] Each answer has 👍 / 👎, and clicking gives a "thanks" message
- [x] The page says it is an AI assistant
- [x] Text is readable (size, contrast); buttons have clear labels
- [x] Works on a phone-width window

## Verification notes

- A 2001-character question shows "Your question is too long (max 2000 characters)." Empty Enter sends no request and does not crash, but shows no message; the combined checklist item remains unchecked.
- Thesis example shows H26#5.3; student-card example shows S26#3.
- The capital-of-France question shows the Training Office escalation note.
- Both feedback actions displayed their thank-you messages and returned HTTP 201. Buttons disappear on the next interaction, not immediately after voting.
- Stopping the API produced "Cannot reach the assistant. Is the backend running?" The API was restarted and a successful answer verified afterward.
- At 390 × 844, the chat, source text, input, and feedback buttons were usable with the sidebar collapsed. The sidebar overlays the chat when open.
- Earlier automated checks: practice 4 passed; starter 49 passed with one dependency deprecation warning (includes 7 UI tests).

## Next: real hallway test

Pending: ask someone outside the team to try the app for two minutes. Record their first name, date, task, and one actual surprise or difficulty. Do not replace their observations with these automated checks.
