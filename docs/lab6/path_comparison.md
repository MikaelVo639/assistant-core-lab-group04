## Dang

### Path Comparison Table (E01–E25)

| path | correct | abstain ok | p50 ms | max ms | fails |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `deterministic` | 9/25 | 7/7 | 0.0 | 1.9 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23 |
| `retrieval` | 18/25 | 5/7 | 0.1 | 0.3 | E13 E14 E15 E19 E21 E22 E24 |
| `llm (stub)` | 18/25 | 5/7 | 0.4 | 1.0 | E13 E14 E15 E19 E21 E22 E24 |

### Analysis (3 sentences)

1. For handbook questions, I would use the **RAG (`rag`)** path (with `min_score` abstain and citation grounding) rather than retrieval-only or direct LLM.
2. It retrieves exact relevant handbook sections, forces the model to cite only retrieved source IDs, and safely abstains when no strong match is found instead of hallucinating.
3. The first failure I would fix is **E14** (`"can I take 32 credits"`), because simple plural stripping (`credits` -> `credit`) in `tokenize` immediately improves keyword matching without risking false positives.

---

### Homework H1: Evaluation with 5 New Cases (E21–E25)
<!-- Re-run `python eval/compare_paths.py` after adding E21–E25 to `eval/cases.jsonl` and paste the updated table here -->

If any of the new questions failed, it is typically because the exact phrasing in the question differs from the keywords in the handbook chunk (or lacks overlapping tokens above `min_score`).

---

### Homework H2: Reflection

Think of RAG like an **open-book exam**: instead of forcing the student (the LLM) to memorize every university rule from memory, we first look up the exact pages from the handbook and hand only those pages to the student to answer. This keeps answers grounded in real, up-to-date facts rather than guesses. One critical thing our code checks that the model does not is **citation grounding** in `parse_draft`—verifying that every cited source ID actually exists in the retrieved `allowed_ids` set (and abstaining before even calling the model if retrieval scores are below `min_score`).


---

## Bonus: H3 (Stripping plural `s` in `tokenize`)

### Before
| path | correct | abstain ok | p50 ms | max ms | fails |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `deterministic` | 9/25 | 7/7 | 0.0 | 1.9 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23 |
| `retrieval` | 18/25 | 5/7 | 0.1 | 0.3 | E13 E14 E15 E19 E21 E22 E24 |
| `llm (stub)` | 18/25 | 5/7 | 0.4 | 1.0 | E13 E14 E15 E19 E21 E22 E24 |

### After
| path | correct | abstain ok | p50 ms | max ms | fails |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `deterministic` | 9/25 | 7/7 | 0.0 | 1.1 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23 |
| `retrieval` | 18/25 | 5/7 | 0.1 | 0.3 | E13 E14 E15 E19 E20 E21 E22 |
| `llm (stub)` | 18/25 | 5/7 | 0.3 | 1.6 | E13 E14 E15 E19 E20 E21 E22 |

### Observation
Stripping a trailing `"s"` from words longer than 4 characters in `tokenize` kept the overall score at **18/25** (`abstain ok: 5/7`). **E14** (`"can I take 32 credits"`) still failed because matching `"credit"` alone is not enough to beat other chunks or reach `min_score = 2.0`. Meanwhile, **E24** started passing, while **E20** (`"tell me about exams"`) began failing because `"exams"` became `"exam"` and matched an existing chunk instead of abstaining.
