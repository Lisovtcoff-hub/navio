# Alembic migrations (Navio) — команды и рабочий процесс (Docker)

Эта памятка для твоего текущего сетапа: **backend + Postgres в Docker Compose**.  
Контейнеры: `navio-backend` и `navio-db` (как у тебя в `docker ps`).

> Цель: быстро и без боли делать миграции Alembic, применять их к БД и проверять результат.

---

## 0) Разовый старт / «сбросить dev-базу и начать чисто» (вариант 1)

⚠️ Удалит ВСЕ данные в dev Postgres (Docker volume).

Из папки `infra/`:

```powershell
docker compose down -v
docker compose up -d --build
```

Проверить, что контейнеры поднялись:

```powershell
docker ps
```

---

## 1) Проверить, что Alembic работает в контейнере backend

```powershell
docker exec -it navio-backend alembic --version
docker exec -it navio-backend alembic current
docker exec -it navio-backend alembic heads
```

Если БД чистая, `alembic current` может показать, что версия не установлена.

---

## 2) Применить существующие миграции на чистую БД

Это нужно делать после `down -v`.

```powershell
docker exec -it navio-backend alembic upgrade head
```

Проверить, что применилось:

```powershell
docker exec -it navio-backend alembic current
```

---

## 3) Основной цикл разработки миграций (каждый раз, когда меняешь модели)

### Шаг A — поменяй модели в коде (на хосте)
Например: `backend/app/models/user.py`.

### Шаг B
с билдом
```powershell
alembic upgrade head
```

```powershell
alembic revision --autogenerate -m "auth"
```

### Шаг C — перезагрузить чтоб применилось
```powershell
docker compose down -v
docker compose up -d --build
```

### Шаг D — проверь, что в БД реально появилось (пример для users)
```powershell
docker exec -it navio-db psql -U navio -d navio -c "\d users"
```

---

## 4) Полезные команды Alembic (на каждый день)

### Текущая применённая ревизия
```powershell
docker exec -it navio-backend alembic current
```

### История миграций (PowerShell)
В PowerShell нет `head`, поэтому:

```powershell
docker exec -it navio-backend alembic history --verbose | Select-Object -First 60
```

### Откатить на 1 миграцию назад (осторожно)
```powershell
docker exec -it navio-backend alembic downgrade -1
```

### Применить до конкретной ревизии
```powershell
docker exec -it navio-backend alembic upgrade 3939cc72057c
```

### Показать SQL, который Alembic собирается выполнить (без выполнения)
```powershell
docker exec -it navio-backend alembic upgrade head --sql | Select-Object -First 120
```

---

## 5) Если autogenerate создаёт «пустую» миграцию

Это обычно значит: Alembic **не видит твои модели** (не подключён `Base.metadata`).

Признак: миграция создана, но внутри почти ничего нет (`pass`).

Что делать:
1) Проверь `backend/alembic/env.py`
2) Там должно быть:
   - `target_metadata = Base.metadata`
   - модели должны импортироваться (часто через импорт `app.models.*`)

> Если хочешь — скинь `backend/alembic/env.py`, и я скажу точный фикс.

---

## 6) Главное правило, чтобы миграции не ломались

- **Не удаляй** файлы из `backend/alembic/versions/`, если миграции уже применялись к БД.
- Если удалил/переименовал и Alembic ругается на “Can't locate revision …” — в dev проще всего:

```powershell
docker compose down -v
docker compose up -d --build
docker exec -it navio-backend alembic upgrade head
```

---

## 7) Шаблон «я поменял модели → хочу миграцию» (копипаст)

```powershell
docker exec -it navio-backend alembic revision --autogenerate -m "describe change"
docker exec -it navio-backend alembic upgrade head
docker exec -it navio-backend alembic current
```

---
