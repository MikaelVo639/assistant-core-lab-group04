# Data model (Lab 5)

Matches `sql/migrations/001_init.sql` and `src/assistant_api/db.py`.

```mermaid
erDiagram
    chat_session ||--o{ interaction : "has"
    interaction  ||--o{ feedback    : "rated by"

    chat_session {
        VARCHAR(16) id PK "salted hash of the session id"
        VARCHAR(16) channel "default 'web'"
        TIMESTAMP created_at
    }
    interaction {
        INTEGER id PK
        VARCHAR(32) request_id UK
        VARCHAR(16) session_id FK "-> chat_session.id"
        VARCHAR(16) intent "indexed"
        VARCHAR(32) topic "nullable, handbook rule id"
        BOOLEAN resolved
        BOOLEAN degraded
        FLOAT latency_ms
        TIMESTAMP created_at "indexed"
    }
    feedback {
        INTEGER id PK
        VARCHAR(32) request_id FK "-> interaction.request_id"
        INTEGER rating "CHECK IN (-1, 0, 1)"
        VARCHAR(500) comment "nullable"
        TIMESTAMP created_at
    }
```

- One `chat_session` has many `interaction` rows (1:N on `interaction.session_id`).
- One `interaction` has zero or more `feedback` rows (1:N on `feedback.request_id`, which references the
  `UNIQUE` `interaction.request_id`). The API returns 404 when the request id does not exist.
- `faq` (migration 002) is standalone staff content with no foreign keys.
- Nothing personal is stored: no raw message, no name or phone, and the session id is a salted hash.
