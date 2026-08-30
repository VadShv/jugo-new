# ATS Jugo — Backend

Applicant Tracking System backend (FastAPI + SQLAlchemy 2.0 async + PostgreSQL).

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e .[dev]
uvicorn jugo.main:app --reload
```

## Checks

```bash
ruff check .
mypy src/jugo
pytest -q
```
