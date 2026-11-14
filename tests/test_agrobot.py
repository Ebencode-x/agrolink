import app as m


def test_history_is_capped_and_ends_with_the_question():
    history = [{"role": "user" if i % 2 == 0 else "bot", "text": f"t{i}"} for i in range(20)]
    out = m.build_agrobot_contents(history, "swali")
    assert len(out) == 7
    assert out[0]["role"] == "user"
    assert out[-1] == {"role": "user", "parts": [{"text": "swali"}]}


def test_roles_alternate_and_leading_bot_turn_is_dropped():
    history = [
        {"role": "bot", "text": "karibu"},
        {"role": "user", "text": "a"},
        {"role": "user", "text": "b"},
    ]
    out = m.build_agrobot_contents(history, "q")
    assert [c["role"] for c in out] == ["user"]
    assert out[0]["parts"][0]["text"] == "a\nb\nq"


def test_html_from_old_bot_replies_is_stripped():
    history = [
        {"role": "user", "text": "nyanya"},
        {"role": "bot", "text": "<strong>Ugonjwa</strong><br>wa nyanya"},
    ]
    out = m.build_agrobot_contents(history, "dawa?")
    assert out[1]["parts"][0]["text"] == "Ugonjwa wa nyanya"


def test_bad_history_values_are_ignored():
    out = m.build_agrobot_contents("not a list", "habari")
    assert out == [{"role": "user", "parts": [{"text": "habari"}]}]
    out = m.build_agrobot_contents([None, 5, {"role": "user", "text": "  "}], "habari")
    assert out == [{"role": "user", "parts": [{"text": "habari"}]}]


import inspect

import pytest

import app as _m


class _Resp:
    def __init__(self, status=200, data=None):
        self.status_code = status
        self.ok = status < 400
        self.text = "x"
        self._data = data

    def json(self):
        return self._data


def _call(monkeypatch, body, post, key="k"):
    monkeypatch.setattr(_m, "GEMINI_API_KEY", key)
    monkeypatch.setattr(_m.requests, "post", post)
    view = inspect.unwrap(_m.agrobot_chat)
    with _m.app.test_request_context("/api/agrobot", method="POST", json=body):
        out = view()
    resp, code = out if isinstance(out, tuple) else (out, 200)
    return resp.get_json(), code


def _ok(*a, **k):
    return _Resp(200, {"candidates": [{"content": {"parts": [{"text": "Jibu zuri"}]}}]})


def test_success_returns_reply_and_key_stays_out_of_the_url(monkeypatch):
    seen = {}

    def post(url, **kwargs):
        seen["url"] = url
        seen["headers"] = kwargs["headers"]
        return _ok()

    data, code = _call(monkeypatch, {"message": "mahindi yanaliwa"}, post)
    assert code == 200 and data["reply"] == "Jibu zuri"
    assert "key=" not in seen["url"]
    assert seen["headers"]["x-goog-api-key"] == "k"


@pytest.mark.parametrize("status", [429, 500, 503])
def test_upstream_errors_ask_the_browser_to_fall_back(monkeypatch, status):
    data, code = _call(monkeypatch, {"message": "habari"}, lambda *a, **k: _Resp(status))
    assert code == 503 and data["fallback"] is True


def test_empty_candidates_fall_back(monkeypatch):
    data, code = _call(monkeypatch, {"message": "habari"}, lambda *a, **k: _Resp(200, {"candidates": []}))
    assert code == 503 and data["fallback"] is True


def test_network_error_falls_back(monkeypatch):
    def boom(*a, **k):
        raise _m.requests.exceptions.ConnectionError("down")

    data, code = _call(monkeypatch, {"message": "habari"}, boom)
    assert code == 503 and data["fallback"] is True


def test_missing_key_falls_back_without_calling_google(monkeypatch):
    def never(*a, **k):
        raise AssertionError("must not call Google without a key")

    data, code = _call(monkeypatch, {"message": "habari"}, never, key="")
    assert code == 503 and data["fallback"] is True


def test_empty_message_is_rejected(monkeypatch):
    data, code = _call(monkeypatch, {"message": "  "}, _ok)
    assert code == 400
