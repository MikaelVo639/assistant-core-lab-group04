# Lab 7 — Usability checklist

The individual branch passed all 4 Streamlit practice tests and all 49 starter tests. Chromium exercised the Streamlit UI against FastAPI with an offline stub and a temporary SQLite database.

- [x] The first screen describes the assistant and offers example questions.
- [x] Empty input leaves the history unchanged. Unit tests verify the empty and overlong validation messages.
- [x] The waiting indicator displays “Thinking…”.
- [x] Grounded answers display their document sources.
- [x] Out-of-scope answers direct the student to the Training Office (I.101).
- [x] An offline API produces a plain-language error.
- [x] Both feedback buttons show confirmation after the API accepts the rating. The same answer cannot be rated again in that session.
- [x] The sidebar identifies the page as an AI assistant.
- [x] Feedback controls have text labels.
- [x] At 390 px width the chat input stays visible and the page has no horizontal overflow.

| Scenario | Observed behavior |
| --- | --- |
| Thesis with 118 credits | The answer gives the 120-credit minimum and cites H26#5.3. |
| Lost student card | Student Affairs, room I.102. |
| Escalation | An out-of-scope question shows a staff contact and room I.101. |
| Degraded answer | A simulated provider failure shows the source-based answer and a fallback note. |
| Rate limit | The sixth question asks the student to wait a minute. |
| Backend offline | A question after stopping the API shows “Cannot reach the assistant.” |

[Successful verification run and screenshots](https://github.com/MikaelVo639/assistant-core-lab-group04/actions/runs/45005880166#artifacts)

Simulated hallway test (Long roleplay): The thesis response gives the minimum but leaves the reader to compare 118 with 120. The lab’s hallway test with a participant from another team is pending.

Team verification (#83) is pending a run from the integrated main after #80 and #82.
