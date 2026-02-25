# 06 — DB schema (Navio) v2 — приоритеты и срезы

Документ описывает **целевую схему БД** для MVP и следующих этапов.  
Формат: **P0/P1/P2** + **вертикальные срезы** (что делать “кусочками”, чтобы быстрее прийти к MVP).

> Технологии: Postgres + SQLAlchemy (sync) + Alembic.  
> Время — `timestamptz`, идентификаторы — `uuid` (как у тебя в текущих моделях).

---

## Принципы (важно)
1) **P0 = только то, что нужно для работающего core-MVP** (auth → тренировка → экзамен → ошибки/прогресс → лидерборд).  
2) **Attempts — единый “лог фактов”**: одна таблица покрывает тренировки и экзамены.  
3) **Целостность важнее “красоты”**: используем FK, UNIQUE, CHECK, индексы по частым запросам.  
4) Любые “фичи вокруг” (teacher mode, лайки, комменты, подписки) — позже.

---

# P0 — MVP Core

## Срез A (P0): Auth + Users
### users
- **id** uuid PK
- **email** text NOT NULL UNIQUE (lowercased в приложении)
- **nickname** text NOT NULL UNIQUE  ← нужен для лидерборда
- **is_teacher** boolean NOT NULL DEFAULT false
- **points** int NOT NULL DEFAULT 0  ← очки для таблицы лидеров
- **created_at** timestamptz NOT NULL DEFAULT now()

Индексы:
- UNIQUE(email)
- UNIQUE(nickname)
- INDEX(points) *(для лидерборда; в Postgres это всё равно может помочь)*

> Рекомендация по UX: ник не участвует в авторизации, но должен быть задан.  
> Для MVP можно: (1) просить ник при первом входе, либо (2) авто-генерировать временный ник и дать поменять.

### login_codes
- **id** uuid PK
- **email** text NOT NULL (index)
- **code_hash** text NOT NULL
- **expires_at** timestamptz NOT NULL
- **consumed_at** timestamptz NULL
- **created_at** timestamptz NOT NULL DEFAULT now()

Индексы:
- INDEX(email, created_at DESC)
- INDEX(email, expires_at)

### refresh_sessions
- **id** uuid PK
- **user_id** uuid NOT NULL FK → users(id) ON DELETE CASCADE
- **refresh_token_hash** text NOT NULL UNIQUE
- **expires_at** timestamptz NOT NULL
- **revoked_at** timestamptz NULL
- **created_at** timestamptz NOT NULL DEFAULT now()

Индексы:
- INDEX(user_id, expires_at)

---

## Срез B (P0): Контент (темы → вопросы → ответы)
### topics
- **id** uuid PK
- **title** text NOT NULL
- **sort_order** int NOT NULL DEFAULT 0
- **created_at** timestamptz NOT NULL DEFAULT now()

### questions
- **id** uuid PK
- **topic_id** uuid NOT NULL FK → topics(id) ON DELETE RESTRICT
- **text** text NOT NULL
- **explanation** text NULL  *(можно хранить кратко; подробности — через lessons в P1)*
- **source** text NULL *(источник/ссылка)*
- **is_active** boolean NOT NULL DEFAULT true
- **created_at** timestamptz NOT NULL DEFAULT now()
- **updated_at** timestamptz NOT NULL DEFAULT now()

Индексы:
- INDEX(topic_id)
- INDEX(is_active)

### answers
- **id** uuid PK
- **question_id** uuid NOT NULL FK → questions(id) ON DELETE CASCADE
- **text** text NOT NULL
- **is_correct** boolean NOT NULL DEFAULT false
- **sort_order** int NOT NULL DEFAULT 0

Ограничения/индексы:
- INDEX(question_id)
- **UNIQUE(id, question_id)**  ← нужно для составного FK из attempts (см. ниже)

> Важно: корректный ответ — один (обычно). Если хочешь жёстко:  
> можно добавить частичный уникальный индекс “только один is_correct=true на вопрос” (P1).

---

## Срез C (P0): Attempts (тренировка + ошибки + прогресс)
### attempts
- **id** uuid PK
- **user_id** uuid NOT NULL FK → users(id) ON DELETE CASCADE
- **question_id** uuid NOT NULL FK → questions(id) ON DELETE RESTRICT
- **answer_id** uuid NULL  *(если “пропуск”, либо не отвечал)*
- **is_correct** boolean NOT NULL
- **mode** text NOT NULL CHECK (mode in ('training','exam')) DEFAULT 'training'
- **exam_id** uuid NULL FK → exams(id) ON DELETE CASCADE  *(появится после добавления exams)*
- **created_at** timestamptz NOT NULL DEFAULT now()

Ключевой constraint (очень важно):
- **FOREIGN KEY (answer_id, question_id) REFERENCES answers(id, question_id)**  
  (требует UNIQUE(id, question_id) в answers)

Индексы:
- INDEX(user_id, created_at DESC)
- INDEX(user_id, is_correct, created_at DESC)
- INDEX(question_id)
- INDEX(exam_id) *(когда появится)*

---

## Срез D (P0): Экзамен (20 вопросов + воспроизводимость)
### exams
- **id** uuid PK
- **user_id** uuid NOT NULL FK → users(id) ON DELETE CASCADE
- **status** text NOT NULL CHECK (status in ('in_progress','finished')) DEFAULT 'in_progress'
- **started_at** timestamptz NOT NULL DEFAULT now()
- **finished_at** timestamptz NULL
- **result_correct** int NOT NULL DEFAULT 0
- **result_wrong** int NOT NULL DEFAULT 0
- **result_passed** boolean NULL

Индексы:
- INDEX(user_id, started_at DESC)
- INDEX(status)

### exam_items
- **exam_id** uuid NOT NULL FK → exams(id) ON DELETE CASCADE
- **question_id** uuid NOT NULL FK → questions(id) ON DELETE RESTRICT
- **position** int NOT NULL CHECK (position >= 0 AND position < 20)
- **created_at** timestamptz NOT NULL DEFAULT now()

PK/ограничения:
- PRIMARY KEY (exam_id, position)
- UNIQUE(exam_id, question_id)

> В attempts для экзамена: mode='exam' и exam_id заполнен.

---

## Срез E (P0): Лидерборд (очки + достижения)
Цель: быстро сделать таблицу лидеров “по очкам” + минимальная аудит-таблица, чтобы очки не были “магией”.

### users.points (уже выше)
- используется для быстрых запросов лидерборда:
  - ORDER BY points DESC, created_at ASC LIMIT 100

### point_events  *(минимальный “ledger”, рекомендую)*
- **id** uuid PK
- **user_id** uuid NOT NULL FK → users(id) ON DELETE CASCADE
- **event_type** text NOT NULL  
  примеры: 'attempt_correct', 'exam_passed', 'daily_streak', 'admin_adjust'
- **delta** int NOT NULL  *(+/-)*
- **meta** jsonb NULL  *(например exam_id, question_id, streak_days)*
- **created_at** timestamptz NOT NULL DEFAULT now()

Индексы:
- INDEX(user_id, created_at DESC)
- INDEX(event_type, created_at DESC)

Логика начисления очков (MVP пример):
- за правильный ответ в тренировке: +1
- за сдачу экзамена: +20
- штраф за неправильный ответ (опционально): 0 или -1

Правило обновления points:
- при вставке point_events приложение в транзакции:
  1) INSERT point_events
  2) UPDATE users SET points = points + delta WHERE id = user_id

Почему так лучше, чем только users.points:
- можно объяснить пользователю “откуда очки”
- проще дебажить и откатывать
- проще защищаться от накрутки (только сервер создаёт события)

---

# P1 — Расширение контента и UX (после core-MVP)

## Срез F (P1): Уроки/материалы + прогресс по урокам
### lessons
- **id** uuid PK
- **topic_id** uuid NULL FK → topics(id) ON DELETE SET NULL
- **title** text NOT NULL
- **kind** text NOT NULL CHECK (kind in ('article','video','link')) DEFAULT 'article'
- **content_url** text NULL
- **content_md** text NULL  *(если хранишь текст локально)*
- **created_at** timestamptz NOT NULL DEFAULT now()
- **updated_at** timestamptz NOT NULL DEFAULT now()

Индексы:
- INDEX(topic_id)

### lesson_progress
- **user_id** uuid NOT NULL FK → users(id) ON DELETE CASCADE
- **lesson_id** uuid NOT NULL FK → lessons(id) ON DELETE CASCADE
- **status** text NOT NULL CHECK (status in ('started','completed')) DEFAULT 'started'
- **started_at** timestamptz NOT NULL DEFAULT now()
- **completed_at** timestamptz NULL

PK:
- PRIMARY KEY (user_id, lesson_id)

---

## Срез G (P1): Нормализация правил ПДД / источников (опционально)
- rules (id, title, body_md, source_url, updated_at)
- topic_rules (topic_id, rule_id) many-to-many

---

## Срез H (P1): Стрики (дни активности) (опционально)
### user_streaks
- **user_id** uuid PK FK → users(id)
- **current_days** int NOT NULL DEFAULT 0
- **best_days** int NOT NULL DEFAULT 0
- **last_active_date** date NULL

---

# P2 — Teacher mode, social, монетизация

## Срез I (P2): Teacher groups
### teacher_groups
- **id** uuid PK
- **owner_user_id** uuid NOT NULL FK → users(id) ON DELETE CASCADE
- **title** text NOT NULL
- **created_at** timestamptz NOT NULL DEFAULT now()

### teacher_group_members
- **group_id** uuid NOT NULL FK → teacher_groups(id) ON DELETE CASCADE
- **user_id** uuid NOT NULL FK → users(id) ON DELETE CASCADE
- **role** text NOT NULL CHECK (role in ('teacher','student')) DEFAULT 'student'
- **created_at** timestamptz NOT NULL DEFAULT now()

PK:
- PRIMARY KEY (group_id, user_id)

---

## Срез J (P2): Custom tests (учительские тесты)
### custom_tests
- **id** uuid PK
- **group_id** uuid NOT NULL FK → teacher_groups(id) ON DELETE CASCADE
- **title** text NOT NULL
- **created_at** timestamptz NOT NULL DEFAULT now()

### custom_test_items
- **custom_test_id** uuid NOT NULL FK → custom_tests(id) ON DELETE CASCADE
- **question_id** uuid NOT NULL FK → questions(id) ON DELETE RESTRICT
- **position** int NOT NULL CHECK (position >= 0)
- PRIMARY KEY (custom_test_id, position)
- UNIQUE(custom_test_id, question_id)

---

## Срез K (P2): Лайки/комменты
- lesson_likes (lesson_id, user_id) PK composite
- question_likes (question_id, user_id) PK composite
- comments (id, user_id, entity_type, entity_id, body, created_at)

---

## Срез L (P2): Подписки/права
- entitlements (user_id, plan, expires_at, created_at)
- purchases (id, user_id, provider, provider_ref, created_at)

---

# План реализации: последовательность и оценка по дням

Оценка — **дни активной разработки**, без пауз.

## Срез A — Auth + Users (1–2 дня)
День 1:
- users: nickname UNIQUE + points + миграция Alembic
- тесты auth flow не сломались
День 2 (если нужно):
- UX для nickname (первый вход / генерация / смена)

## Срез B — Контент (1–2 дня)
День 1:
- привести topics/questions/answers к схеме (индексы, updated_at)
День 2:
- seed/import контента + тесты

## Срез C — Attempts (2 дня)
День 1:
- attempts + составной FK (answer_id, question_id) + миграция + тесты
День 2:
- training API (next/answer) + начисление очков (point_events) за correct

## Срез D — Exams (2–3 дня)
День 1:
- exams, exam_items + миграция
- start exam: создать 20 items
День 2:
- next/answer + запись attempts с exam_id
- подсчёт результата
День 3 (опционально):
- усложнённые правила “добавочных вопросов” (можно отложить)

## Срез E — Лидерборд (1–2 дня)
День 1:
- point_events + транзакционная функция начисления
- начисление за exam_passed
День 2:
- endpoint leaderboard + тесты + пагинация

## Итого P0: 7–11 дней
- Быстро: ~7–8 дней
- Реалистично: ~9–11 дней

---
# P1 (контент + UX)

## Срез F — lessons + lesson_progress: 2–3 дня
- День 1: таблицы + миграция + CRUD минимально
- День 2: прогресс (started/completed) + эндпоинты + тесты
- День 3 (опц.): “рекомендовать урок при ошибке” (по topic_id), полировка

## Срез G — rules + topic_rules (опционально): 2–4 дня
- День 1: tables + миграция
- День 2–3: импорт/seed правил + API чтения
- День 4 (опц.): связывание с вопросами/темами более умно

## Срез H — streaks (опционально): 1–2 дня
- День 1: таблица + логика обновления при активности
- День 2 (опц.): начисление очков/streak events + тесты

## Итого P1:
- минимально (только lessons+progress): 2–3 дня
- типично (lessons + rules или streaks): 4–7 дней
- полно (lessons + rules + streaks): 6–10 дней

# P2 (teacher mode + social + монетизация)

## Срез I — teacher_groups + members: 2–3 дня
- День 1: таблицы + миграции
- День 2: API (create group, invite/join, list members) + тесты
- День 3 (опц.): роли/права аккуратно

## Срез J — custom_tests + items: 2–4 дня
- День 1: таблицы + миграции
- День 2: API (create test, add items)
- День 3: прохождение custom test (можно reuse exam flow)
- День 4 (опц.): отчёты/статистика по группе

## Срез K — лайки/комменты: 2–5 дней
- лайки: 1–2 дня
- комменты: ещё 1–3 дня (модерация можно позже)

## Срез L — entitlements/purchases (монетизация, опционально): 3–7 дней
- зависит от провайдера, webhooks, валидаций

## Итого P2:
- teacher-mode минимум (groups + custom tests без отчётов): 4–7 дней
- social: 6–12 дней
- монетизация: 9–19 дней
---

# Примечание: “введите никнейм или почту” (без усложнения)
Минимально:
- request-code принимает `identifier`
- если есть `@` → email
- иначе → nickname → ищем users.nickname → берём users.email
- ответ: “код отправлен на t***@gmail.com” (masked_email)
- при неизвестном нике/почте возвращаем одинаковый ответ (не палим существование)

---
