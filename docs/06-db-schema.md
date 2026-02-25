# Navio — DB Schema (MVP)

Цель MVP: тренировка/экзамен/ошибки/прогресс + материалы (уроки/видео) + минимальный teacher-mode (группы + кастомные тесты) + лайки/комменты.

> Все временные поля: `timestamptz`.
> PK: `uuid` (генерация на стороне приложения или `gen_random_uuid()`).
> Строковые enum-поля в MVP допустимы, но лучше добавить CHECK constraints.

---

## 1) users

**users**
- `id` uuid PK
- `email` text NOT NULL UNIQUE
- `nickname` text NOT NULL UNIQUE
- `created_at` timestamptz NOT NULL DEFAULT now()

- `is_plus` boolean NOT NULL DEFAULT false
- `is_teacher` boolean NOT NULL DEFAULT false

- `days_streak` int NOT NULL DEFAULT 0  _(optional cache; можно считать по фактам)_
- `lessons_passed` int NOT NULL DEFAULT 0 _(optional cache; можно считать по lesson_progress)_

Indexes:
- UNIQUE(email)
- UNIQUE(nickname)

**login_codes**
- `id` uuid PK
- `email` text NOT NULL
- `code_hash` text NOT NULL (храним не сам код, а хэш)
- `purpose` text NOT NULL DEFAULT 'login' (login, signup)
- `created_at` timestamptz NOT NULL DEFAULT now()
- `expires_at` timestamptz NOT NULL (например +10 минут)
- `attempts_left` int NOT NULL DEFAULT 5
- `consumed_at` timestamptz NULL
- `ip` text NULL
- `user_agent` text NULL

Indexes:
- INDEX(email, created_at DESC)
- INDEX(expires_at)

**refresh_sessions**
- `id` (uuid)
- `user_id` (fk)
- `token_hash`
- `created_at`
- `expires_at`
- `revoked_at` (nullable)

---

## 2) topics

**topics**
- `id` uuid PK
- `title` text NOT NULL UNIQUE

Indexes:
- UNIQUE(title)

---

## 3) questions / answers

**questions**
- `id` uuid PK
- `topic_id` uuid NOT NULL FK -> topics(id)
- `text` text NOT NULL
- `image_url` text NULL
- `explanation_short` text NULL
- `explanation_full` text NULL
- `source_version` text NULL
- `updated_at` timestamptz NOT NULL DEFAULT now()

Indexes:
- INDEX(topic_id)
- INDEX(updated_at)

**answers**
- `id` uuid PK
- `question_id` uuid NOT NULL FK -> questions(id) ON DELETE CASCADE
- `text` text NOT NULL
- `is_correct` boolean NOT NULL DEFAULT false

Indexes:
- INDEX(question_id)
- (optional) UNIQUE(question_id) WHERE is_correct=true  _(если гарантируем 1 правильный ответ)_

---

## 4) attempts (самая “горячая” таблица)

**attempts**
- `id` uuid PK
- `user_id` uuid NOT NULL FK -> users(id) ON DELETE CASCADE
- `question_id` uuid NOT NULL FK -> questions(id)
- `answer_id` uuid NOT NULL FK -> answers(id)

- `is_correct` boolean NOT NULL
- `mode` text NOT NULL  _(training|exam)_
- `exam_id` uuid NULL FK -> exams(id) ON DELETE SET NULL

- `created_at` timestamptz NOT NULL DEFAULT now()
- `time_spent_ms` int NULL  _(опционально, если нужен тайминг)_

Constraints:
- CHECK (mode in ('training','exam'))

Indexes (MVP MUST HAVE):
- INDEX(user_id, created_at DESC)                         -- лента попыток/последние ответы
- INDEX(user_id, is_correct, created_at DESC)             -- ошибки/неправильные
- INDEX(user_id, question_id)                             -- контроль повторов / анти-спам повторов
- INDEX(exam_id)                                          -- ответы экзамена
- INDEX(user_id, mode, created_at DESC)                   -- фильтрация по режиму

---

## 5) exams + exam_items

**exams**
- `id` uuid PK
- `user_id` uuid NOT NULL FK -> users(id) ON DELETE CASCADE
- `started_at` timestamptz NOT NULL DEFAULT now()
- `finished_at` timestamptz NULL
- `status` text NOT NULL DEFAULT 'in_progress'  _(in_progress|passed|failed)_

Constraints:
- CHECK (status in ('in_progress','passed','failed'))

Indexes:
- INDEX(user_id, started_at DESC)

**exam_items** (фиксирует состав экзамена)
- `exam_id` uuid NOT NULL FK -> exams(id) ON DELETE CASCADE
- `question_id` uuid NOT NULL FK -> questions(id)
- `position` int NOT NULL  _(0..19)_

PK/Constraints:
- PRIMARY KEY (exam_id, position)
- UNIQUE (exam_id, question_id)

Indexes:
- INDEX(exam_id)
- INDEX(question_id)

---

## 6) lessons / lesson_progress

**lessons**
- `id` uuid PK
- `topic_id` uuid NOT NULL FK -> topics(id)
- `title` text NOT NULL
- `text` text NULL
- `video_url` text NULL  _(tiktok-like, youtube, s3 link etc.)_
- `created_at` timestamptz NOT NULL DEFAULT now()
- `updated_at` timestamptz NOT NULL DEFAULT now()

Indexes:
- INDEX(topic_id)
- INDEX(updated_at)

**lesson_progress**
- `user_id` uuid NOT NULL FK -> users(id) ON DELETE CASCADE
- `lesson_id` uuid NOT NULL FK -> lessons(id) ON DELETE CASCADE
- `status` text NOT NULL DEFAULT 'started'  _(started|completed)_
- `updated_at` timestamptz NOT NULL DEFAULT now()

PK/Constraints:
- PRIMARY KEY (user_id, lesson_id)
- CHECK (status in ('started','completed'))

Indexes:
- INDEX(user_id, updated_at DESC)
- INDEX(lesson_id)

---

## 7) comments + likes (чтобы лайки не “врали”)

**comments**
- `id` uuid PK
- `lesson_id` uuid NOT NULL FK -> lessons(id) ON DELETE CASCADE
- `user_id` uuid NOT NULL FK -> users(id) ON DELETE CASCADE
- `text` text NOT NULL
- `created_at` timestamptz NOT NULL DEFAULT now()

Indexes:
- INDEX(lesson_id, created_at DESC)        -- список комментариев урока
- INDEX(user_id, created_at DESC)

**lesson_likes**
- `lesson_id` uuid NOT NULL FK -> lessons(id) ON DELETE CASCADE
- `user_id` uuid NOT NULL FK -> users(id) ON DELETE CASCADE
- `created_at` timestamptz NOT NULL DEFAULT now()

PK/Constraints:
- PRIMARY KEY (lesson_id, user_id)

**comment_likes**
- `comment_id` uuid NOT NULL FK -> comments(id) ON DELETE CASCADE
- `user_id` uuid NOT NULL FK -> users(id) ON DELETE CASCADE
- `created_at` timestamptz NOT NULL DEFAULT now()

PK/Constraints:
- PRIMARY KEY (comment_id, user_id)

> Примечание: `likes_count` в lessons/comments можно хранить как кеш (денорм),
> но источник истины — таблицы likes. Для MVP можно считать count(*) по likes.

---

## 8) entitlements / подписка (Plus)

MVP-версия: можно держать `users.is_plus`, а историю — в отдельной таблице.

**plus_entitlements**
- `id` uuid PK
- `user_id` uuid NOT NULL FK -> users(id) ON DELETE CASCADE
- `started_at` timestamptz NOT NULL
- `ends_at` timestamptz NULL
- `source` text NULL _(manual|google|apple|promo)_
- `created_at` timestamptz NOT NULL DEFAULT now()

Indexes:
- INDEX(user_id, started_at DESC)
- (optional) INDEX(ends_at)

> В MVP допускается включать/выключать Plus админом, а платежи — Post-MVP.

---

## 9) teacher mode: группы + membership

**teacher_groups**
- `id` uuid PK
- `teacher_id` uuid NOT NULL FK -> users(id) ON DELETE CASCADE
- `name` text NOT NULL
- `description` text NULL
- `img_link` text NULL
- `created_at` timestamptz NOT NULL DEFAULT now()

Indexes:
- INDEX(teacher_id, created_at DESC)
- UNIQUE(teacher_id, name)

**teacher_group_members**
- `group_id` uuid NOT NULL FK -> teacher_groups(id) ON DELETE CASCADE
- `user_id` uuid NOT NULL FK -> users(id) ON DELETE CASCADE
- `joined_at` timestamptz NOT NULL DEFAULT now()

PK/Constraints:
- PRIMARY KEY (group_id, user_id)

Indexes:
- INDEX(user_id)
- INDEX(group_id)

> Это лучше, чем `users.teacher_group_id`, потому что пользователь может быть в нескольких группах.

---

## 10) custom tests (teacher)

**custom_tests**
- `id` uuid PK
- `owner_user_id` uuid NOT NULL FK -> users(id) ON DELETE CASCADE   _(учитель/создатель)_
- `group_id` uuid NULL FK -> teacher_groups(id) ON DELETE SET NULL  _(если тест для группы)_

- `title` text NOT NULL
- `config_json` jsonb NOT NULL  _(вопросы/темы/настройки)_
- `questions_count` int NOT NULL DEFAULT 0   _(денорм, для удобства)_

- `allowed_attempts` int NULL
- `time_limit_sec` int NULL

- `link_token` text NOT NULL UNIQUE  _(короткий токен для ссылки)_
- `is_active` boolean NOT NULL DEFAULT true

- `created_at` timestamptz NOT NULL DEFAULT now()
- `starts_at` timestamptz NULL
- `ends_at` timestamptz NULL

Indexes:
- INDEX(owner_user_id, created_at DESC)
- INDEX(group_id)
- UNIQUE(link_token)

**custom_test_attempts**
- `id` uuid PK
- `custom_test_id` uuid NOT NULL FK -> custom_tests(id) ON DELETE CASCADE
- `user_id` uuid NOT NULL FK -> users(id) ON DELETE CASCADE

- `created_at` timestamptz NOT NULL DEFAULT now()
- `finished_at` timestamptz NULL

- `score` int NOT NULL DEFAULT 0
- `errors_count` int NOT NULL DEFAULT 0
- `result_json` jsonb NULL          _(подробности: ответы/ошибки, MVP ok)_

Indexes:
- INDEX(custom_test_id, created_at DESC)
- INDEX(user_id, created_at DESC)

---

## 11) Минимальные замечания про производительность (ориентир 100k MAU)

1) Основной рост — `attempts`. Индексы выше обязательны.
2) Для “прогресса” лучше использовать агрегаты:
   - на MVP можно считать on-demand за последние N дней
   - post-MVP: таблица `user_topic_stats` или materialized view.
3) JSONB допустим в `custom_tests.config_json` и `custom_test_attempts.result_json` в MVP,
   но для глубокой аналитики лучше нормализовать ошибки в отдельную таблицу позже.

---

## 12) Non-goals MVP (схема не включает)
- Платёжные транзакции (чеки, подписки Google/Apple) — Post-MVP
- Полный RAG/AI — Post-MVP
- Сложные достижения/ачивки — Post-MVP (можно считать из attempts/lesson_progress)