from tests.helpers import seed_login_code


def test_signup_requires_valid_nickname(client, db):
    email = "nickbad@example.com"
    code = seed_login_code(db, email)

    resp = client.post(
        "/api/v1/auth/verify-code",
        json={"identifier": email, "code": code, "nickname": "!"},
    )
    assert resp.status_code == 400
    # у тебя текст может отличаться — проверяй по началу
    assert "Nickname required" in resp.json()["detail"]


def test_signup_nickname_taken_returns_409(client, db):
    # создадим первого юзера
    email1 = "one@example.com"
    code1 = seed_login_code(db, email1)
    r1 = client.post(
        "/api/v1/auth/verify-code",
        json={"identifier": email1, "code": code1, "nickname": "capy_same"},
    )
    assert r1.status_code == 200, r1.text

    # второй юзер пытается взять тот же ник
    email2 = "two@example.com"
    code2 = seed_login_code(db, email2)
    r2 = client.post(
        "/api/v1/auth/verify-code",
        json={"identifier": email2, "code": code2, "nickname": "capy_same"},
    )
    assert r2.status_code == 409, r2.text
    assert r2.json()["detail"] == "Nickname already taken"
