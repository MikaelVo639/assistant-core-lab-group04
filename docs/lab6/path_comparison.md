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