# Lab 5 verification

Validated on 2026-11-13 from `lab05/starter` (Python 3.12, pinned `requirements.txt`).

- Practice: `python check.py <file>` scores 15/15 for every `my_answers*.sql` (Man, Minh, Dat, Thang,
  Thinh); `pytest -q ../practice` passes 5 (D1-D3, including the injection test).
- Starter: `pytest -q tests` passes 29, including R1/R2, the 404 for an unknown request id and
  `test_feedback_survives_restart` (a second app on the same SQLite file still lists the feedback).
- Ruff lint and format checks pass; CI runs them for lab04 and lab05 in the `labs` job.

## Part E.6: feedback survives a restart

A real `uvicorn` server on a fresh database: chat returns a `request_id`, feedback for it returns 201,
an unknown id returns 404, and after stopping and starting the server the admin list still has the
feedback. The database holds only `chat_session`, `interaction` and `feedback`; the session id is a
salted hash and no raw message or name is stored. Full output: [feedback-persistence.txt](feedback-persistence.txt).

Reproduce (PowerShell, from `lab05/starter`):

```powershell
$env:PYTHONPATH = "src"; $env:API_ADMIN_KEY = "demo-key"
python -m uvicorn assistant_api.main:create_app --factory
```

## Part F and H2

Queries are in `lab05/starter/sql/my_queries.sql`, with results on the 300-row seed
(`python scripts/migrate.py assistant.db` then `python scripts/seed.py assistant.db 300`):
F1 rule 140, fee 61, office 47, greeting 26, unknown 26; H2 unresolved: unknown 26; H2 degraded share: 38/300 = 12.67%.

The design review (H3) is in `lab05/worksheets/data_model.md` with the ER diagram in
`lab05/starter/docs/data-model.md`.
