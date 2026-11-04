import os

from app import app as flask_app


def test_session_cookie_flags():
    assert flask_app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert flask_app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert flask_app.config["SESSION_COOKIE_SECURE"] is bool(os.environ.get("RENDER"))


def test_remember_cookie_flags():
    assert flask_app.config["REMEMBER_COOKIE_HTTPONLY"] is True
    assert flask_app.config["REMEMBER_COOKIE_SAMESITE"] == "Lax"
    assert flask_app.config["REMEMBER_COOKIE_SECURE"] is bool(os.environ.get("RENDER"))
