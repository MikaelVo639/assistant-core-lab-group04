# Bootstrap verification

Verified on 2026-10-24 at the requested final directory using Python 3.12.14.

This verifies the repository starting point, not a completed Lab 03 service.

| Check | Result |
| --- | --- |
| Original Lab 03 files | All 5 match upstream Git blob hashes, on disk and in the first commit |
| Working CSV/JSON data | Both byte-identical to the original |
| Original --test demo | Exit 0; greeting, fee and office outputs checked |
| python -m pytest -q | 9 passed; deterministic characterisation tests of the original monolith |
| python -m ruff check . | All checks passed; original teaching monolith explicitly excluded |
| python -m ruff format --check . | All checked Python files already formatted |
| python -m pip check | No broken requirements found |
| Installed package import with -I | Resolves to this repo's src/assistant_core/__init__.py |
| .env / .venv | Ignored by Git |
| Branch / remotes | main; no GitHub remote configured |

Installed versions: pydantic==2.9.2, python-dotenv==1.0.1, pytest==8.3.3, ruff==0.6.9.

Next: each member completes their own refactor and PR; later integrate one group version.
The new service, its CLI, tests of its modules, GitHub collaboration settings and completion tags remain pending.
