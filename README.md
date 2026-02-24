# Navio 🚗💨
**Navio** — приложение и сайт для подготовки к теоретическому экзамену ПДД/ГИБДД РФ:  
адаптивная тренировка, экзамен как в ГИБДД, понятные объяснения и ассистент (строго по источникам).

## Что в репозитории
- `apps/mobile` — Flutter (Android/iOS)
- `apps/web` — Web (Next.js)
- `backend` — API (FastAPI)
- `content` — контент: темы/правила/объяснения/уроки
- `docs` — план, UX, API-контракт, схема БД, релиз-чеклисты
- `infra` — инфраструктура (docker-compose, деплой и т.п.)

## Быстрый старт (локально)

### 1) Backend (FastAPI)
**Требования:** Python 3.11+  
```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Healthcheck:
- http://localhost:8000/api/v1/health

### 2) Docker (backend + Postgres)

```bash
cd infra
cp ../backend/.env.example ../backend/.env
docker compose up --build
```
