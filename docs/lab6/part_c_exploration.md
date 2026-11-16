# Lab 6 Part C — Searching the knowledge base

I searched the 14 document sections with BM25 and requested up to two results per question.

| Question | Top chunk | BM25 score |
|---|---|---:|
| How do I reset my IT account password? | `S26#2` — IT account password reset | 10.311 |
| I forgot my login details. How can I get back in? | No match (`[]`) | N/A |
| Can I register my thesis after the deadline? | `H26#5.3` — Thesis registration | 4.005 |

**Observation.** For the late thesis question, payment deadline (`F26#3`, 3.831) unexpectedly came second. It shares the word “deadline” with the question, while the section on late thesis registration fell outside the top two.