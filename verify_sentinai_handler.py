"""Check the SentinAI log handler against a fake ingest server on this machine.

Run:  venv/bin/python verify_sentinai_handler.py
Nothing is sent to production.
"""

import json
import logging
import os
import sys
import threading
import time
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from flask import Flask
from sqlalchemy.exc import IntegrityError

import sentinai_handler

KEY = "snl_" + "k" * 32
os.environ.pop("RENDER", None)
os.environ["FLASK_ENV"] = "staging"
os.environ["RENDER_GIT_COMMIT"] = "abc123def456"
received = []
failures = []
script = []


class FakeIngest(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        received.append((dict(self.headers), body))
        status = script.pop(0) if script else 202
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        if status == 429:
            self.send_header("Retry-After", "30")
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, *args):
        return


def check(label, condition):
    print(("[OK] " if condition else "[FAIL] ") + label)
    if not condition:
        failures.append(label)
    return condition


def require(label, condition):
    if not check(label, condition):
        print(f"[STOP] {len(failures)} check(s) failed")
        sys.exit(1)


def wait_for(predicate, timeout=6.0):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if predicate():
            return True
        time.sleep(0.05)
    return predicate()


def all_events():
    return [event for _, body in received for event in body["events"]]


def is_uuid(value):
    try:
        return str(uuid.UUID(value)) == value
    except (ValueError, TypeError, AttributeError):
        return False


def is_utc_timestamp(value):
    try:
        return datetime.fromisoformat(value).utcoffset() is not None
    except (ValueError, TypeError):
        return False


server = ThreadingHTTPServer(("127.0.0.1", 0), FakeIngest)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{server.server_port}/api/v1/events"

# 1. install() gating
os.environ.pop("SENTINAI_INGEST_URL", None)
os.environ.pop("SENTINAI_INGEST_KEY", None)
check("no env vars: no handler", sentinai_handler.install(Flask("probe_a")) is None)
os.environ["SENTINAI_INGEST_KEY"] = KEY
os.environ["SENTINAI_INGEST_URL"] = "http://example.com/api/v1/events"
check(
    "plain http to a remote host is refused",
    sentinai_handler.install(Flask("probe_b")) is None,
)
os.environ["SENTINAI_INGEST_URL"] = "https://example.com/api/ingest"
check("the old ingest path is refused", sentinai_handler.install(Flask("probe_c")) is None)
os.environ["SENTINAI_INGEST_URL"] = "https://example.com/api/v1/events"
os.environ["SENTINAI_INGEST_KEY"] = "k" * 32
check("a key without the snl_ prefix is refused", sentinai_handler.install(Flask("probe_d")) is None)
os.environ["SENTINAI_INGEST_KEY"] = KEY

# 2. a real Flask app with an errorhandler(500) like AgroLink
os.environ["SENTINAI_INGEST_URL"] = url
app = Flask("verify_app")


@app.errorhandler(500)
def server_error(error):
    return "oops", 500


@app.route("/boom")
def boom():
    raise KeyError("missing")


@app.route("/db")
def db_failure():
    raise IntegrityError(
        "INSERT INTO users (email, name) VALUES (%(email)s, %(name)s)",
        {"email": "a@b.com", "name": "Juma"},
        Exception("duplicate key, Key (email)=(a@b.com) already exists."),
    )


handler = sentinai_handler.install(app)
require("handler installed for a local url", handler is not None)
handler._flush_seconds = 0.2
client = app.test_client()

response = client.get("/boom")
check("the user still gets the 500 page", response.status_code == 500)
require("an event reaches the fake SentinAI", wait_for(lambda: len(received) >= 1))
headers, body = received[0]
event = body["events"][0]
check("bearer header is sent", headers.get("Authorization") == f"Bearer {KEY}")
check("the old key header is gone", "X-Ingest-Key" not in headers)
check("source is not in the body (it comes from the key)", "source" not in body)
check("event_id is a uuid", is_uuid(event.get("event_id")))
check("level is error", event.get("level") == "error")
check("exception_type is KeyError", event.get("exception_type") == "KeyError")
check("timestamp is ISO 8601 with a timezone", is_utc_timestamp(event.get("timestamp")))
check("environment comes from FLASK_ENV", event.get("environment") == "staging")
check("release comes from RENDER_GIT_COMMIT", event.get("release") == "abc123def456")
check("message names the failing path", "Exception on /boom" in event["message"])
trace = event.get("stacktrace", "")
check("full traceback is attached", "Traceback (most recent call last):" in trace)
check("exception line is attached", "KeyError: 'missing'" in trace)

# 3. database exception messages are withheld
before = len(all_events())
client.get("/db")
require("db error event arrives", wait_for(lambda: len(all_events()) > before))
sent_text = json.dumps(all_events()[before:])
check("db message is withheld", "<message withheld>" in sent_text)
check("no email in what was sent", "a@b.com" not in sent_text)
check("no name in what was sent", "Juma" not in sent_text)

# 4. size limits are respected, so one big event cannot break a batch
before = len(all_events())
try:
    raise ValueError("y" * 20000)
except ValueError:
    app.logger.error("z" * 5000, exc_info=True)
require("big event arrives", wait_for(lambda: len(all_events()) > before))
big = all_events()[before]
check("message is within 1000 chars", len(big["message"]) <= 1000)
check("traceback is within 6000 chars", len(big.get("stacktrace", "")) <= 6000)

# 5. bursts are split into batches of at most 20
before = len(all_events())
for i in range(45):
    app.logger.error("burst %d", i)
check("all 45 burst events arrive", wait_for(lambda: len(all_events()) - before == 45))
check("no batch is larger than 20", all(len(b["events"]) <= 20 for _, b in received))

# 6. SentinAI unreachable: no blocking, sending pauses after repeated failures
dead = sentinai_handler.SentinAIHandler(
    "http://127.0.0.1:1/api/v1/events", KEY, flush_seconds=0.05, retry_delay=0.01
)
dead_logger = logging.getLogger("verify_dead")
dead_logger.propagate = False
dead_logger.addHandler(dead)
started = time.monotonic()
for i in range(300):
    dead_logger.error("dead %d", i)
elapsed = time.monotonic() - started
check("300 errors with SentinAI down take under 1 second", elapsed < 1.0)
check("sending pauses after repeated failures", wait_for(
    lambda: dead._paused_until > time.monotonic()
))
check("dropped events are counted", wait_for(lambda: dead.dropped > 0))

# 7. retries and error handling (statuses are scripted on the fake server)
def probe(name):
    probe_handler = sentinai_handler.SentinAIHandler(
        url, KEY, flush_seconds=0.05, retry_delay=0.01
    )
    probe_logger = logging.getLogger(name)
    probe_logger.propagate = False
    probe_logger.addHandler(probe_handler)
    return probe_handler, probe_logger


script[:] = [503, 202]
before = len(received)
retry_handler, retry_logger = probe("verify_retry")
retry_logger.error("retry me")
check("a 503 is retried and then accepted", wait_for(lambda: retry_handler.sent == 1))
ids = {b["events"][0]["event_id"] for _, b in received[before:]}
check("the retry reuses the same event_id", len(received) - before == 2 and len(ids) == 1)

script[:] = [401]
before = len(received)
auth_handler, auth_logger = probe("verify_401")
auth_logger.error("bad key")
check("a 401 is dropped", wait_for(lambda: auth_handler.dropped == 1))
time.sleep(0.3)
check("a 401 is not retried", len(received) - before == 1)

script[:] = [422]
before = len(received)
bad_handler, bad_logger = probe("verify_422")
bad_logger.error("bad shape")
check("a 422 is dropped", wait_for(lambda: bad_handler.dropped == 1))
time.sleep(0.3)
check("a 422 is not retried", len(received) - before == 1)
check("a 422 does not pause sending", bad_handler._paused_until <= time.monotonic())

script[:] = [429]
limited_handler, limited_logger = probe("verify_429")
limited_logger.error("too many")
check(
    "a 429 pauses for the time the server asks",
    wait_for(lambda: limited_handler._paused_until > time.monotonic() + 20),
)

server.shutdown()
if failures:
    print(f"[RESULT] {len(failures)} check(s) failed")
    sys.exit(1)
print("[RESULT] all checks passed")
