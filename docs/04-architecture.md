# Architecture (MVP)

## Клиенты
- Mobile: Flutter (Android; iOS позже)
- Web: Next.js (лендинг + web-тренажёр)

## Backend
- FastAPI (Python)
- Postgres (данные)
- Redis (кеш/лимиты) — можно добавить после MVP, но лучше заложить
- Object storage (S3/R2) для картинок вопросов

## Основные принципы
- Вся логика “экзамена и проверки” на backend (единая правда)
- Клиенты тонкие: UI + кеш + вызовы API
- Ассистент в MVP не генерирует “из головы”, только из базы

## Поток данных (пример)
Training next -> API -> question
Attempt -> API -> save attempt + compute stats -> return result + explanation
AI explain -> API -> assemble answer from explanations/rules -> return structured response

## Деплой (MVP)
- Backend: VPS + Docker (или managed)
- Web: Vercel/Pages
- Storage: S3/R2
- Monitoring: Sentry
