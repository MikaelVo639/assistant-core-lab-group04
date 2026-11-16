# Lab 6 path comparison

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

## Dat

### Path comparison (E01-E25, before my H1 cases)

| path | correct | abstain ok | p50 ms | max ms | fails |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `deterministic` | 9/25 | 7/7 | 0.0 | 0.6 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23 |
| `retrieval` | 18/25 | 5/7 | 0.0 | 0.1 | E13 E14 E15 E19 E21 E22 E24 |
| `llm (stub)` | 18/25 | 5/7 | 0.2 | 0.6 | E13 E14 E15 E19 E21 E22 E24 |

For handbook questions I would use the RAG path: retrieval with the `min_score` abstain and the citation check in front of the model. It gets twice as many questions right as the keyword rules (18 vs 9), and every answer points to a section a student can open and check. The first failure I would fix is E19 ("is the final exam open-book"): it does not just miss, it confidently cites the exam-absence rule (H26#7.2) for a question the documents never answer, and a wrong answer with a real-looking source is worse than saying "I don't know".

### H1: five new cases (E26-E30)

| id | question | expected |
| :--- | :--- | :--- |
| E26 | can I renew a library book online | `S26#1` |
| E27 | what GPA do I need to register a thesis | `H26#5.3` |
| E28 | how many semesters can I take a leave of absence | `H26#8.1` |
| E29 | show me my roommate's exam schedule | abstain (privacy) |
| E30 | recommend a good laptop for programming | abstain (out of scope) |

Re-run with E01-E30:

| path | correct | abstain ok | p50 ms | max ms | fails |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `deterministic` | 11/30 | 9/9 | 0.0 | 0.7 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23 E26 E27 E28 |
| `retrieval` | 21/30 | 6/9 | 0.0 | 0.1 | E13 E14 E15 E19 E21 E22 E24 E26 E29 |
| `llm (stub)` | 21/30 | 6/9 | 0.2 | 0.6 | E13 E14 E15 E19 E21 E22 E24 E26 E29 |

E26 failed because the rule-based router sees "library" and returns the library's room and opening hours before retrieval runs. E29 failed because the privacy guard only blocks "roommate" next to grade/score/gpa/result/phone/address, so "exam schedule" slips through and BM25 cites the unrelated exam-absence rule.

### H2: reflection

RAG is like an open-book exam: the model is the student, and the handbook is the book on the desk.
Before the student writes anything, we find the two or three pages that match the question and hand over only those pages.
The student must answer from those pages and write down which page each fact came from, instead of answering from memory.
If no page matches well enough, the student hands in a blank sheet that says "ask the Training Office" instead of guessing.
One thing our code checks that the model does not: in `parse_draft`, every cited source id must be one of the retrieved pages, otherwise the answer is rejected.

---

## Thinh

### Path Comparison Baseline (`E01–E20`)

| path | correct | abstain ok | p50 ms | max ms | fails |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `deterministic` | 7/20 | 5/5 | 0.0 | 0.4 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 |
| `retrieval` | 16/20 | 4/5 | 0.0 | 0.1 | E13 E14 E15 E19 |
| `llm (stub)` | 16/20 | 4/5 | 0.2 | 0.6 | E13 E14 E15 E19 |

### Path Comparison Analysis (3 sentences)

For handbook questions, I would use the **RAG (`llm`)** path with `min_score` abstention before the model call and citation validation afterwards.
It grounds answers in retrieved policy chunks, blocks fabricated or unretrieved `source_ids` via `parse_draft`, and degrades safely to quoting the top chunk if the provider fails.
First, I would fix **E14** (`"can I take 32 credits"`) by normalizing simple plural inflections such as `credits` -> `credit` in tokenization so paraphrased rule queries score above `min_score` without weakening abstention.

### Homework H1: Evaluation with 5 New Cases (`E31–E35`, 35 Cases Total on Branch)

| path | correct | abstain ok | p50 ms | max ms | fails |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `deterministic` | 13/35 | 11/11 | 0.0 | 0.4 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23 E26 E27 E28 E31 E32 E33 |
| `retrieval` | 26/35 | 8/11 | 0.0 | 0.1 | E13 E14 E15 E19 E21 E22 E24 E26 E29 |
| `llm (stub)` | 26/35 | 8/11 | 0.2 | 0.5 | E13 E14 E15 E19 E21 E22 E24 E26 E29 |

All five of Thinh's new cases (`E31–E35`) passed on both `retrieval` and `llm (stub)`, while `E31–E33` failed only on `deterministic` because it does not search the markdown knowledge base (and earlier failures like `E26` and `E29` occurred because router office keywords or unmatched privacy nouns bypassed KB retrieval or the regex guard).

### Homework H2: Reflection (5 lines)

RAG works like an open-book exam where the retriever finds the relevant handbook pages first and hands only those pages to the model.
The language model's job is simply to phrase a concise answer from the excerpts it was given, rather than guessing rules from memory.
Before calling the model at all, our code checks `hits[0].score < self.min_score` in `RagAnswerer` and immediately abstains if no section is relevant enough.
After the model replies, `parse_draft` enforces strict JSON validation and rejects any response whose cited `source_ids` are empty or outside the retrieved `allowed_ids` set.
The model only generates candidate text and cannot reliably police itself against hallucinated citations or unanswerable queries without those deterministic checks in code.

---

## Minh

### Original 20 cases

| Path | Correct | Correct abstentions | p50 (ms) | Max (ms) | Failed cases |
| --- | ---: | ---: | ---: | ---: | --- |
| Deterministic | 7/20 | 5/5 | 0.0 | 0.5 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 |
| Retrieval | 16/20 | 4/5 | 0.0 | 0.0 | E13 E14 E15 E19 |
| LLM (stub) | 16/20 | 4/5 | 0.2 | 6.3 | E13 E14 E15 E19 |

I would use the retrieval path for handbook questions. It quotes the official text and matches the stub's accuracy on this set with lower measured latency. I would fix E19 first because the exam-absence section scores 5.620 for “is the final exam open-book” even though it gives no guidance on exam format.

### H1 evaluation with E36–E40

| Path | Correct | Correct abstentions | p50 (ms) | Max (ms) | Failed cases |
| --- | ---: | ---: | ---: | ---: | --- |
| Deterministic | 9/25 | 7/7 | 0.0 | 0.4 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E36 E37 E38 |
| Retrieval | 21/25 | 6/7 | 0.0 | 0.1 | E13 E14 E15 E19 |
| LLM (stub) | 21/25 | 6/7 | 0.2 | 0.4 | E13 E14 E15 E19 |

All five new questions passed on retrieval and stub, while the deterministic path missed E36–E38 because it has no handbook and campus-services retrieval.

### H2 reflection

1. RAG works like an open-book exam where the official handbook is the book.
2. Before answering, the assistant searches for the passages that match the question.
3. The model uses those passages as notes and cites them in its answer.
4. When the best passage scores below the threshold, the assistant says it is unsure before calling the model.
5. Our code independently checks that every answer cites at least one of the passages it actually retrieved.

---

## Man

### Original 20 cases

| Path | Correct | Correct abstentions | Median latency (ms) | Maximum latency (ms) | Failed cases |
|---|---:|---:|---:|---:|---|
| Deterministic | 7/20 | 5/5 | 0.0 | 1.0 | E01, E02, E05, E06, E07, E08, E09, E10, E11, E12, E13, E14, E15 |
| Retrieval | 16/20 | 4/5 | 0.0 | 0.1 | E13, E14, E15, E19 |
| LLM (stub) | 16/20 | 4/5 | 0.1 | 1.1 | E13, E14, E15, E19 |

I would use retrieval for handbook questions because students can read the cited passage directly.
Retrieval and the stub both scored 16/20 and missed the same four cases, and retrieval had the lowest maximum latency in this run.
I would fix E19 first because the assistant should abstain when a passage about exam absence is retrieved for a question about open-book exams.

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
