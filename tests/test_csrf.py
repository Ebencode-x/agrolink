import app as appmod


def test_post_without_token_is_rejected_when_csrf_enabled():
    appmod.app.config["WTF_CSRF_ENABLED"] = True
    client = appmod.app.test_client()
    r = client.post("/login", json={"phone": "x", "password": "y"})
    assert r.status_code == 400


def test_payment_callback_is_exempt_from_csrf():
    appmod.app.config["WTF_CSRF_ENABLED"] = True
    client = appmod.app.test_client()
    r = client.post("/payments/callback", json={})
    assert r.status_code != 400 or "Ombi halikukubaliwa" not in r.get_data(as_text=True)
