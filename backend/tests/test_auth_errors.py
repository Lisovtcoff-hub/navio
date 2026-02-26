import pytest
from sqlalchemy import select

from app.models.login_code import LoginCode
from tests.helpers import seed_login_code_custom


@pytest.mark.parametrize(
    "case, code_sent, code_entered, expires_in_seconds, attempts_left, expected_detail",
    [
        ("wrong_code", "111111", "222222", 600, 5, "Invalid code"),
        ("expired", "111111", "111111", -10, 5, "Code expired"),
        ("too_many_attempts", "111111", "111111", 600, 0, "Too many attempts"),
    ],
)
def test_verify_code_errors(
    client,
    db,
    case,
    code_sent,
    code_entered,
    expires_in_seconds,
    attempts_left,
    expected_detail,
):
    email = "err@example.com"

    seed_login_code_custom(
        db,
        email=email,
        code=code_sent,
        expires_in_seconds=expires_in_seconds,
        attempts_left=attempts_left,
    )

    resp = client.post(
        "/api/v1/auth/verify-code",
        json={"identifier": email, "code": code_entered, "nickname": "capy_err"},
    )
    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"] == expected_detail


def test_wrong_code_decrements_attempts_left(client, db):
    email = "attempts@example.com"
    seed_login_code_custom(db, email=email, code="111111", expires_in_seconds=600, attempts_left=5)

    resp = client.post(
        "/api/v1/auth/verify-code",
        json={"identifier": email, "code": "000000", "nickname": "capy_x"},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Invalid code"

    # проверим, что attempts_left уменьшился
    row = (
        db.execute(
            select(LoginCode)
            .where(LoginCode.email == email)
            .order_by(LoginCode.created_at.desc())
            .limit(1)
        )
        .scalars()
        .first()
    )
    assert row is not None
    assert row.attempts_left == 4
