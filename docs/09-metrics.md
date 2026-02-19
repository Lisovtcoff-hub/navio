# Metrics & Analytics (MVP)

## KPI продукта
- Activation: пользователь решил ≥20 вопросов в первый день
- Retention D1/D7
- Learning success: 3 “passed” экзамена подряд
- Time-to-success: сколько дней до стабильной сдачи

## События (events)
- auth_signup
- auth_login
- training_start
- training_answer (properties: is_correct, topic_id, has_image)
- ai_explain_open
- exam_start
- exam_answer (is_correct)
- exam_finish (passed/failed, score)
- mistakes_open
- progress_open

## Минимальные свойства
- platform (android/web)
- app_version
- user_id (анонимный id если без регистрации)
