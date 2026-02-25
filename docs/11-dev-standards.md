# Dev standards (Navio)

## Python style
- Formatter/Linter: Ruff
- Python: 3.11+
- Import style: Ruff (без isort отдельно)
- Line length: 100
- Type hints: по возможности для публичных функций (API/сервисы)

## Commands (backend)
Из папки backend:

- Format:
  - ruff format .
- Lint:
  - ruff check .
- Tests:
  - pytest -q

## Errors (API)
Все ошибки возвращаем в одном формате:

{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}

Примеры code:
- validation_error
- unauthorized
- forbidden
- not_found
- conflict
- rate_limited
- internal_error