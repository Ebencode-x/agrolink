from datetime import datetime

import app as m
import server
import wsgi


def test_wsgi_and_server_expose_the_app():
    # gunicorn wsgi:app depends on this import, ruff must never remove it
    assert wsgi.app is m.app
    assert server.app is m.app


def test_month_names_cover_the_year():
    # NameError here broke /api/listing-advice in production
    assert len(m.MONTH_NAMES_SW) == 12
    assert m.MONTH_NAMES_SW[datetime.utcnow().month - 1]


def test_health_is_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_ubia_is_rate_limited_per_ip(client):
    codes = [client.post("/ubia", data={"website_url": "x"}).status_code for _ in range(4)]
    assert codes == [302, 302, 302, 429]


def test_listing_advice_requires_login(client):
    response = client.post("/api/listing-advice", json={"crop_name": "mahindi"})
    assert response.status_code in (301, 302, 401)
