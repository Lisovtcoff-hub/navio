# DB Schema (черновик MVP)

## users
- id (uuid)
- email (unique)
- password_hash
- created_at

## topics
- id (uuid)
- title
- slug
- parent_id (nullable)

## questions
- id (uuid)
- text
- image_url (nullable)
- explanation_short (nullable)
- explanation_full (nullable)
- source_version (nullable)
- updated_at

## answers
- id (uuid)
- question_id (fk)
- text
- is_correct (bool)

## question_topics
- question_id (fk)
- topic_id (fk)

## attempts
- id (uuid)
- user_id (fk)
- question_id (fk)
- answer_id (fk)
- is_correct (bool)
- mode (training/exam)
- exam_id (nullable)
- created_at

## exams
- id (uuid)
- user_id (fk)
- started_at
- finished_at (nullable)
- status (in_progress/passed/failed)

## exam_questions
- id (uuid)
- exam_id (fk)
- question_id (fk)
- order (int)
- user_answer_id (nullable)
- is_correct (nullable)

## user_topic_stats (агрегаты)
- user_id (fk)
- topic_id (fk)
- correct_count
- wrong_count
- mastery (float 0..1) (optional)
- updated_at
