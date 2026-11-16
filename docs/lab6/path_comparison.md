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

## Thang

### Path Comparison Table (Baseline E01–E30)

| path | correct | abstain ok | p50 ms | max ms | fails |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `deterministic` | 11/30 | 9/9 | 0.0 | 0.9 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23 E26 E27 E28 |
| `retrieval` | 21/30 | 6/9 | 0.1 | 0.1 | E13 E14 E15 E19 E21 E22 E24 E26 E29 |
| `llm (stub)` | 21/30 | 6/9 | 0.3 | 0.9 | E13 E14 E15 E19 E21 E22 E24 E26 E29 |

### Analysis (3 sentences)
1. For handbook questions, I would choose the **RAG (`llm`)** path with strict citation grounding and confidence thresholding over keyword matching or raw retrieval.
2. It allows students to ask complex, natural-language questions while constraining the LLM to cite only actual retrieved official handbook sections and gracefully abstaining when evidence is insufficient.
3. The first failure I would fix is **E14** (`"can I take 32 credits"`), because normalizing plural nouns (e.g. stemming `credits` to `credit` in tokenization) would immediately bridge the lexical gap between the student's question and chunk `H26#6.1`.

---

### Homework H1: Five New Cases (E36–E40)

| id | question | expected | category |
| :--- | :--- | :--- | :--- |
| E36 | how much is the replacement fee for a lost student card | `S26#3` | normal |
| E37 | where can I reset my university account password | `S26#2` | normal |
| E38 | what is the deadline for final-year students to register retakes | `H26#4.2` | normal |
| E39 | what was my classmate's GPA last semester | abstain | privacy |
| E40 | what is the weather like in Tokyo tomorrow | abstain | out-of-scope |

#### Updated Path Comparison Table (E01–E40, 35 cases)

| path | correct | abstain ok | p50 ms | max ms | fails |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `deterministic` | 13/35 | 11/11 | 0.0 | 0.7 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23 E26 E27 E28 E36 E37 E38 |
| `retrieval` | 25/35 | 8/11 | 0.1 | 0.2 | E13 E14 E15 E19 E21 E22 E24 E26 E29 E36 |
| `llm (stub)` | 25/35 | 8/11 | 0.2 | 0.7 | E13 E14 E15 E19 E21 E22 E24 E26 E29 E36 |

**Failure Analysis for New Cases:**
E36 failed under retrieval because the presence of the word "fee" gave heavier lexical BM25 weight to retake fee policy (`F26#2`) rather than the student card replacement service (`S26#3`), demonstrating that isolated keyword overlap can overshadow the true semantic intent when multiple service documents share administrative terms.

---

### Homework H2: Reflection (5 lines)

1. RAG is like an open-book exam: rather than relying on the student's memory (which might hallucinate or recall outdated facts), we provide relevant textbook pages right on their desk.
2. Before the student begins answering, our system locates the two or three exact passages matching the prompt and feeds only those excerpts to the model.
3. The student is required to synthesize an answer exclusively from those excerpts and explicitly reference the corresponding section number for each stated fact.
4. If no passage meets the minimum relevance threshold, the system immediately returns a refusal message rather than allowing the model to make wild guesses.
5. One crucial check our code enforces that the model cannot is citation grounding: `parse_draft` strictly validates that every cited source ID belongs to the retrieved `allowed_ids` set, raising a `ProviderError` if the model hallucinates a reference.
