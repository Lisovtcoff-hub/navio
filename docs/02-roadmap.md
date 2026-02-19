# Roadmap (MVP ~60 рабочих дней, 5ч/день)

## Фаза 0 — Старт и рамки (Дни 1–3)
- Репо + структура
- Docs (vision/scope/roadmap/ux)
- Название/маскот зафиксированы (Navio + капибара)
- Черновой UX (потоки экранов)

## Фаза 1 — Backend core (Дни 4–10)
- FastAPI проект + healthcheck
- Postgres + Alembic
- Модели: topics/questions/answers/attempts/exams
- API: тренировка/попытки/экзамен
- Импорт контента (JSON/CSV)
- AI MVP: explain_mistake без генерации

## Фаза 2 — Mobile MVP (Flutter) (Дни 11–30)
- Auth (welcome/login/signup)
- Home
- Training flow
- Mistakes
- Progress (простая аналитика)
- Exam flow
- Beta Android build

## Фаза 3 — Web MVP (Next.js) (Дни 31–42)
- Лендинг
- Auth
- Web тренировка/экзамен
- Deploy (домен + SSL)

## Фаза 4 — Качество и релизная готовность (Дни 43–55)
- Тестирование, багфиксы
- Политики (privacy/terms)
- Sentry/Crashlytics/analytics events
- Оптимизация медиа/кеш
- Финальные тексты стор/скриншоты

## Фаза 5 — Релиз (Дни 56–60)
- Google Play Console
- Internal testing -> Production
- Проверка веба (SEO базовое, метрики)
- План первой недели (фидбек + hotfix)

## После MVP (ориентир)
- v1: умная тренировка, SEO темы, улучшение контента, кабинет преподавателя (частично)
- v2: обучение “карточки/шорты”, расширенная аналитика, монетизация
