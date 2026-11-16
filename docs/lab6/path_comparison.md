# Lab 6 path comparison

## Minh

### Original 20 cases

| Path | Correct | Correct abstentions | p50 (ms) | Max (ms) | Failed cases |
| --- | ---: | ---: | ---: | ---: | --- |
| Deterministic | 7/20 | 5/5 | 0.0 | 0.5 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 |
| Retrieval | 16/20 | 4/5 | 0.0 | 0.0 | E13 E14 E15 E19 |
| LLM (stub) | 16/20 | 4/5 | 0.2 | 6.3 | E13 E14 E15 E19 |

I would use the retrieval path for handbook questions. It quotes the official text and matches the stub's accuracy on this set with lower measured latency. I would fix E19 first because the exam-absence section scores 5.620 for “is the final exam open-book” even though it gives no guidance on exam format.

### H1 evaluation with E26–E30

| Path | Correct | Correct abstentions | p50 (ms) | Max (ms) | Failed cases |
| --- | ---: | ---: | ---: | ---: | --- |
| Deterministic | 9/25 | 7/7 | 0.0 | 0.4 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E26 E27 E28 |
| Retrieval | 21/25 | 6/7 | 0.0 | 0.1 | E13 E14 E15 E19 |
| LLM (stub) | 21/25 | 6/7 | 0.2 | 0.4 | E13 E14 E15 E19 |

All five new questions passed on retrieval and stub, while the deterministic path missed E26–E28 because it has no handbook and campus-services retrieval.

### H2 reflection

1. RAG works like an open-book exam where the official handbook is the book.
2. Before answering, the assistant searches for the passages that match the question.
3. The model uses those passages as notes and cites them in its answer.
4. When the best passage scores below the threshold, the assistant says it is unsure before calling the model.
5. Our code independently checks that every answer cites at least one of the passages it actually retrieved.
