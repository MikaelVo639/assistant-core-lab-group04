# Lab 7 homework — usability test notes

Participant: Long (assistant roleplay). This is a simulated walkthrough of the H1 scenario. The required 10-minute session with a real participant from outside the team is pending.

Task: “Find out if you can register your thesis with 118 credits, and where to replace a lost student card.”

| # | Simulated observation | Expected behavior | Why the UI caused it | Fix idea |
|---|---|---|---|---|
| 1 | Long reads the 120-credit minimum, then rereads the question to check whether 118 qualifies. | See the eligibility decision first. | The answer quotes the general rule and leaves the comparison to the reader. | Lead with the decision for 118 credits, then show the minimum and citation. |
| 2 | Long expects the source title under the thesis answer to open the handbook. | Inspect the cited section in one action. | The answer shows a source ID and title as plain text. | Link to the section when a stable official URL is available. |
| 3 | Long returns to the answer after the feedback toast disappears and is unsure whether the vote was saved. | See the received state beside the same answer. | After confirmation, the rating buttons disappear and the acknowledgement is temporary. | Keep a text caption below a rated answer. |

Implemented the third fix. The app displays “Feedback recorded.” on the rated answer after the API accepts the vote.

- [Fix commit](https://github.com/MikaelVo639/assistant-core-lab-group04/commit/22339554d700319e49b843e6de2beac3816fc905)
- [Before — negative-feedback.png](https://github.com/MikaelVo639/assistant-core-lab-group04/actions/runs/45005880166#artifacts)
- [After — feedback-after.png](https://github.com/MikaelVo639/assistant-core-lab-group04/actions/runs/45006957971#artifacts)
