# Navio 🚗💨

[![Backend CI](https://github.com/Lisovtcoff-hub/navio/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/Lisovtcoff-hub/navio/actions)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![Flutter](https://img.shields.io/badge/Flutter-3.x-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

**Navio** — open-source платформа для подготовки к теоретическому экзамену ПДД/ГИБДД РФ.

- 🎯 Адаптивная тренировка  
- 📝 Экзамен как в ГИБДД (20 вопросов)  
- 📊 Прогресс и слабые темы  
- 📚 Уроки и видео-разборы  
- 👩‍🏫 Teacher mode (группы и кастомные тесты)

Проект находится в стадии активной разработки (MVP).

---

## 📦 Архитектура

Mobile (Flutter)

→ Backend (FastAPI) → PostgreSQL
/
Web (Next.js)

- **Backend** — FastAPI + PostgreSQL  
- **Mobile** — Flutter (Android / iOS)  
- **Web** — Next.js  
- **Infrastructure** — Docker Compose  
- **CI** — GitHub Actions  

---

## 📂 Структура репозитория

````
apps/
mobile/        # Flutter приложение
web/           # Web-клиент (Next.js)

backend/         # API (FastAPI)
content/         # Контент (вопросы, темы, уроки)
docs/            # Документация (архитектура, API, БД и т.д.)
infra/           # Docker, инфраструктура
.github/         # CI/CD
````

---

## 🚀 Быстрый старт

### Backend (локально)

**Требования:** Python 3.11+

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements-dev.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
````

Healthcheck:

```
http://localhost:8000/api/v1/health
```

---

### Backend + Postgres (Docker)

```bash
cd infra
cp ../backend/.env.example ../backend/.env
docker compose up --build
```

---

## 🧪 Development

### Lint & Format

```bash
ruff check .
ruff format .
```

### Tests

```bash
pytest -q
```

CI автоматически проверяет:

* форматирование (ruff)
* линтинг
* тесты (pytest)

---

## 🔐 Авторизация

MVP использует passwordless-подход:

* вход по коду из письма
* JWT access token
* refresh sessions

---

## 🗺️ Roadmap (MVP)

* [x] Монорепозиторий
* [x] GitHub Actions (CI)
* [x] Авторизация
* [ ] Тренировка
* [ ] Экзамен
* [ ] Teacher mode
* [ ] Прогресс
* [ ] Android release
* [ ] iOS release

---

## 🤝 Contributing

Contributions are welcome.

1. Fork repository
2. Create feature branch
3. Commit changes
4. Open Pull Request

Перед созданием PR убедитесь, что:

* код проходит `ruff`
* тесты проходят `pytest`
* изменения описаны в PR

---

## 📄 License

This project is licensed under the MIT License.

---

© Navio

