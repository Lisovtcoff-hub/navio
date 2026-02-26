def test_request_code_unknown_nickname_does_not_reveal(client, db):
    resp = client.post("/api/v1/auth/request-code", json={"identifier": "no_such_nick"})
    assert resp.status_code == 200
    assert resp.json()["masked_email"] == "***"


def test_verify_code_unknown_nickname_returns_invalid_code(client, db):
    # мы не сидим login_code вообще, потому что email неизвестен
    resp = client.post(
        "/api/v1/auth/verify-code", json={"identifier": "no_such_nick", "code": "123456"}
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Invalid code"
