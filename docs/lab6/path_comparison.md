# Lab 6 — Comparison on the original 20 questions

## Man

| Path | Correct | Correct abstentions | Median latency (ms) | Maximum latency (ms) | Failed cases |
|---|---:|---:|---:|---:|---|
| Deterministic | 7/20 | 5/5 | 0.0 | 1.0 | E01, E02, E05, E06, E07, E08, E09, E10, E11, E12, E13, E14, E15 |
| Retrieval | 16/20 | 4/5 | 0.0 | 0.1 | E13, E14, E15, E19 |
| LLM (stub) | 16/20 | 4/5 | 0.1 | 1.1 | E13, E14, E15, E19 |

I would use retrieval for handbook questions because students can read the cited passage directly.
Retrieval and the stub both scored 16/20 and missed the same four cases, and retrieval had the lowest maximum latency in this run.
I would fix E19 first because the assistant should abstain when a passage about exam absence is retrieved for a question about open-book exams.

### H1 — Five additional questions

E46–E48 cover book renewal, late thesis approval, and password recovery. E49 asks about an opera outside the documents, and E50 asks for another student's GPA.

| Path | Correct | Correct abstentions | Median latency (ms) | Maximum latency (ms) | Failed cases |
|---|---:|---:|---:|---:|---|
| Deterministic | 9/25 | 7/7 | 0.0 | 0.6 | E01, E02, E05, E06, E07, E08, E09, E10, E11, E12, E13, E14, E15, E46, E47, E48 |
| Retrieval | 21/25 | 6/7 | 0.0 | 0.1 | E13, E14, E15, E19 |
| LLM (stub) | 21/25 | 6/7 | 0.2 | 14.2 | E13, E14, E15, E19 |

The rules-only path missed E46–E48 because those questions require a passage from the documents, while retrieval and the stub passed all five new cases.

### H2 — Explaining RAG to a friend

Imagine taking an open-book exam with the student handbook on your desk.<br>
When you get a question, you first look for a passage that might answer it.<br>
Our assistant does that search and gives the model the passages it finds.<br>
The model uses them to write its answer, and our code checks that every source it cites was actually retrieved.<br>
If the search finds too little evidence, the assistant says it cannot answer and directs the student to someone who can help.
