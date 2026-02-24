# Backend (FastAPI)

## Requirements
- Python 3.11+

## Quick start (Windows PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Healthcheck:
- http://localhost:8000/api/v1/health

## Lint & tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
ruff format app tests
ruff check app tests
pytest -q
```
