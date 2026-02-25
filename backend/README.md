# Navio Backend — Solo Dev Workflow (cheatsheet)

Этот документ — “как работать каждый день” соло-разработчику: что запускать, откуда запускать, какие команды и зачем.

> Все команды ниже предполагают, что ты находишься в корне репозитория `navio/`, если не сказано иначе.

---

## 0) Структура и “откуда запускать”

- **backend/** — код FastAPI, зависимости, тесты, миграции (Alembic)
- **infra/** — docker-compose для сервисов (Postgres, backend и т.п.)

Правило:
- команды Python (`pytest`, `ruff`, `alembic`, `uvicorn`) — **запускай из `backend/`**
- команды Docker (`docker compose ...`) — **запускай из `infra/`**

---

## 1) Быстрый старт (локально без Docker)

### 1.1 Установка окружения (один раз)
Из `backend/`:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```
### 1.2 Запуск сервера
```
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Проверка:

- http://localhost:8000/api/v1/health
- Swagger: http://localhost:8000/docs

---

## 2) Запуск через Docker (backend + Postgres)
### 2.1 Поднять сервисы

Из infra/:
```
cd infra
docker compose up --build
```
### 2.2 Остановить сервисы
```
cd infra
docker compose down
```
### 2.3 Полный сброс БД (удалит данные)
```
cd infra
docker compose down -v
```
---

## 3) Логи Docker (как смотреть)
### 3.1 Логи backend

Из infra/:
```
cd infra
docker compose logs -f backend
```
### 3.2 Логи Postgres
```
cd infra
docker compose logs -f db
```
### 3.3 Логи по контейнеру (если знаешь имя)
```
docker logs -f navio-backend
docker logs -f navio-db
```
---
## 4) Миграции БД (Alembic)

Alembic команды запускай из backend/.
База должна быть поднята (обычно через docker compose up).

### 4.1 Сгенерировать новую миграцию

Когда ты добавил/изменил модели в app/models/:
```
cd backend
alembic revision --autogenerate -m "meaningful message"
```
Пример:
```
alembic revision --autogenerate -m "add login codes"
```
### 4.2 Применить миграции
```
cd backend
alembic upgrade head
```
### 4.3 Посмотреть текущую версию схемы
```
cd backend
alembic current
```
### 4.4 Посмотреть историю миграций
```
cd backend
alembic history
```
Если используешь Docker и миграции нужно прогнать внутри контейнера
```
docker exec -it navio-backend bash
alembic upgrade head
exit
```
---
## 5) Тесты (pytest)
### 5.1 Запустить все тесты

Из backend/:
```
cd backend
pytest
```
### 5.2 Запустить один файл
```
cd backend
pytest tests/test_health.py
```
### 5.3 Запустить тесты тихо
```
cd backend
pytest -q
```
### 5.4 Запустить по фильтру имени
```
cd backend
pytest -k health
```

Зачем pytest:

- проверяет, что API работает как ожидалось

- ловит регрессии (сломал — тест упал)

---
## 6) Ruff (format + lint)

Ruff = formatter + linter.

### 6.1 Форматирование кода (приводит код к единому стилю)

Из backend/:
```
cd backend
ruff format .
```
### 6.2 Линтинг (ищет ошибки и плохие практики)
```
cd backend
ruff check .
```
### 6.3 Авто-исправления (например, импорты, мелкие проблемы)
```
cd backend
ruff check . --fix
```

Рекомендуемый порядок перед коммитом:
```
cd backend
ruff format .
ruff check . --fix
pytest
```
---
## 7) Финальный рабочий процесс соло-разработчика (как продолжать самому)
Когда добавляешь новую фичу (пример: training)

1. Schemas (DTO)

    `app/schemas/training.py` — модели запросов/ответов

2. Routes (эндпоинты)

    `app/api/v1/routes/training.py` — HTTP слой (получить данные → вызвать логику → вернуть ответ)

3. Подключить роутер

    `app/api/v1/router.py` — include_router(training_router)

4. DB Models (если нужна таблица)

    `app/models/*.py` — SQLAlchemy модели

5. Миграция
```
cd backend
alembic revision --autogenerate -m "add training tables"
alembic upgrade head
```

6. Тесты

    `tests/test_training.py` — тесты на новые endpoints

7. Проверка перед пушем
```
cd backend
ruff format .
ruff check . --fix
pytest
```
8. Запуск

- локально: `uvicorn ...`

- или docker: `docker compose up --build`

---
## 8) Полезные проверки
### Healthcheck API

- http://localhost:8000/api/v1/health

### Swagger UI

- http://localhost:8000/docs

---
## 9) Частые проблемы
### “relation does not exist”
Ты написал код, который использует таблицу, но не применил миграции:
- alembic upgrade head

### “No module named app”
Ты запускаешь команды не из backend/:
- cd backend и запускай оттуда

### Docker “старые данные”
Нужно сбросить volume:
- docker compose down -v

---
## 10) Команды-минимум (короткий набор)

### Запуск системы
```
cd infra
docker compose up --build
```
### Логи
```
cd infra
docker compose logs -f backend
```
### Миграции
```
cd backend
alembic upgrade head
```
### Качество перед коммитом
```
cd backend
ruff format .
ruff check . --fix
pytest
```
```
::contentReference[oaicite:0]{index=0}
```