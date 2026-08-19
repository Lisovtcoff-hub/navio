# Navio

[![Backend CI](https://github.com/lisovcoff/navio/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/lisovcoff/navio/actions/workflows/backend-ci.yml)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Backend-first monorepo for a driving theory exam preparation product focused on Russian traffic rules. The implemented part of the repository is the FastAPI backend; `apps/mobile` and `apps/web` currently reserve the structure for planned client applications.

## Highlights

- passwordless authentication with email codes, JWT access tokens, and refresh sessions;
- PostgreSQL persistence with Alembic migrations;
- local backend development workflow and Docker-based backend plus PostgreSQL environment;
- pytest, Ruff, and GitHub Actions checks for the backend;
- product scope, roadmap, UX flows, and data model documentation under `docs/`.

## Stack

`Python 3.11` · `FastAPI` · `PostgreSQL` · `SQLAlchemy` · `Alembic` · `Pytest` · `Ruff` · `Docker Compose` · `GitHub Actions`

## Architecture

```text
Planned mobile / web clients
            |
       FastAPI backend
            |
        PostgreSQL
```

The backend is the current production of work in this repository. Client directories are present as monorepo placeholders and product structure, but do not yet contain implemented applications.

## Run locally

Backend only:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check: `http://localhost:8000/api/v1/health`

Docker environment:

```bash
cd infra
cp ../backend/.env.example ../backend/.env
docker compose up --build
```

## Development and tests

```bash
cd backend
ruff check .
ruff format .
pytest -q
alembic upgrade head
```

## Repository layout

```text
backend/         FastAPI application, migrations, and tests
apps/mobile/     reserved structure for planned Flutter client
apps/web/        reserved structure for planned web client
content/         study content and related assets
docs/            product, roadmap, UX, architecture, and data notes
infra/           Docker Compose environment
```

## Product docs

- vision: [docs/00-vision.md](docs/00-vision.md)
- MVP scope: [docs/01-mvp-scope.md](docs/01-mvp-scope.md)
- roadmap: [docs/02-roadmap.md](docs/02-roadmap.md)
- data model: [docs/06-db-schema.md](docs/06-db-schema.md)

## Notes

- This repository is backend-first today; mobile and web client implementation is planned, not shipped.
- The project is licensed under the MIT License.
