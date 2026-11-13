# Lab 5 — Data model worksheet

## 1. Critique the bad schema (sql/bad_schema.sql)
| # | Problem | Why it hurts | Fix |
|---|---|---|---|
| 1 | Student names and phone numbers repeat on every chat. | These identifiers expose students without helping measure service quality. | Omit both and group interactions by a salted session hash. |
| 2 | Ratings share one comma-separated text field. | Counting negative ratings requires parsing text. | Store one numeric rating per feedback row and link it to the interaction by request ID. |
| 3 | Latency contains units in a text field. | Computing an average requires parsing every value. | Store milliseconds in the numeric latency_ms column. |
| 4 | `id INTEGER` is not a primary key. | Duplicate or NULL ids are allowed, so a row cannot be referenced reliably. | `id INTEGER PRIMARY KEY` on every table, plus a `UNIQUE` `request_id` that feedback can point to. |
| 5 | The raw message and answer are kept forever. | Messages can contain personal data, and nothing in the product needs the text itself. | Store only metadata (intent, topic, resolved, degraded, latency); never the raw message or answer. |
| 6 | `intent` is free text ('fee', 'Fee', 'tuition'). | The same intent splits into several groups, so `GROUP BY intent` gives wrong counts. | A short, indexed `intent` column written only by the router from a fixed set of values. |
| 7 | `time` is locale text ('5/10/2026 9:03 PM'). | Text does not sort or filter by date correctly. | A `TIMESTAMP` `created_at` set by the server in UTC, indexed for time-range queries. |

## 2. Store or not? (privacy-aware storage)
| Data | Store? | Form (raw / hashed / aggregated / none) | Retention | Reason |
|---|---|---|---|---|
| raw user message | No | none | not kept | No feature needs the text, and it may contain personal data. |
| session id | Yes | hashed (salted, 16 hex chars) | same as interactions | Groups one conversation's interactions without revealing who it was. |
| intent, latency, topic | Yes | raw metadata per interaction | one semester, then aggregate | Powers the quality questions in section 3. |
| feedback rating | Yes | raw (-1 / 0 / 1, `CHECK` constraint) | one semester, then aggregate | Measures answer quality per intent and topic. |
| feedback comment | Yes, optional | raw, max 500 chars | one semester | Explains a bad rating. The UI must warn users not to type personal data. |
| student name / phone | No | none | not kept | Not needed for any feature; storing it breaks the "store only what a feature needs" rule. |

## 3. Product questions → fields
| Product question | Fields needed | Table(s) | Query sketch |
|---|---|---|---|
| Most failed intent? | `intent`, `resolved` | `interaction` | `SELECT intent, SUM(resolved = 0) AS failed FROM interaction GROUP BY intent ORDER BY failed DESC` |
| Average response time by intent? | `intent`, `latency_ms` | `interaction` | `SELECT intent, ROUND(AVG(latency_ms), 1) FROM interaction GROUP BY intent` |
| Top unresolved topics? | `topic`, `resolved` | `interaction` | `SELECT topic, COUNT(*) AS n FROM interaction WHERE resolved = 0 AND topic IS NOT NULL GROUP BY topic ORDER BY n DESC` |

## 4. ER diagram
Draw entities, keys and relationships (photo or Mermaid in docs/data-model.md).

See [starter/docs/data-model.md](../starter/docs/data-model.md).
