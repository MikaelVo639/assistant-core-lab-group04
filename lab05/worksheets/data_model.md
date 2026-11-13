# Lab 5 — Data model worksheet

## 1. Critique the bad schema (sql/bad_schema.sql)
| # | Problem | Why it hurts | Fix |
|---|---|---|---|
| 1 | Student names and phone numbers repeat on every chat. | These identifiers expose students without helping measure service quality. | Omit both and group interactions by a salted session hash. |
| 2 | Ratings share one comma-separated text field. | Counting negative ratings requires parsing text. | Store one numeric rating per feedback row and link it to the interaction by request ID. |
| 3 | Latency contains units in a text field. | Computing an average requires parsing every value. | Store milliseconds in the numeric latency_ms column. |
| 4 | | | |
| 5 | | | |
| 6 | | | |

## 2. Store or not? (privacy-aware storage)
| Data | Store? | Form (raw / hashed / aggregated / none) | Retention | Reason |
|---|---|---|---|---|
| raw user message | | | | |
| session id | | | | |
| intent, latency, topic | | | | |
| feedback rating | | | | |
| feedback comment | | | | |
| student name / phone | | | | |

## 3. Product questions → fields
| Product question | Fields needed | Table(s) | Query sketch |
|---|---|---|---|
| Most failed intent? | | | |
| Average response time by intent? | | | |
| Top unresolved topics? | | | |

## 4. ER diagram
Draw entities, keys and relationships (photo or Mermaid in docs/data-model.md).
