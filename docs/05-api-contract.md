# API Contract (черновик MVP)

База URL: /api/v1

## Auth
POST /auth/signup
- req: { email, password }
- res: { access_token, refresh_token? }

POST /auth/login
- req: { email, password }
- res: { access_token, refresh_token? }

POST /auth/refresh
- req: { refresh_token }
- res: { access_token }

POST /auth/logout
- res: 204

GET /me
- res: { id, email, created_at }

## Training
GET /training/next?mode=random|smart
- res: QuestionDTO

POST /attempts
- req: { question_id, answer_id, mode: "training"|"exam", exam_id? }
- res: {
    is_correct,
    correct_answer_id,
    explanation_short,
    topic_ids[]
  }

GET /mistakes
- res: [QuestionBriefDTO]

POST /mistakes/{question_id}/reset
- res: 204

## Exam
POST /exams/start
- req: { mode: "gibdd" }
- res: { exam_id }

GET /exams/{exam_id}
- res: { exam_id, status, started_at, questions: [QuestionDTO], progress }

POST /exams/{exam_id}/answer
- req: { question_id, answer_id }
- res: { is_correct, correct_answer_id, explanation_short }

POST /exams/{exam_id}/finish
- res: { status: "passed"|"failed", score, mistakes: [QuestionBriefDTO], weak_topics: [TopicDTO] }

## AI (MVP без генерации)
POST /ai/explain_mistake
- req: { question_id, user_answer_id }
- res: {
    title,
    short,
    details,
    common_mistake,
    mnemonic,
    sources: [{type: "topic"|"rule", id, title}]
  }
