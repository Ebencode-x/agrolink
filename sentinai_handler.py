"""Forward ERROR level log records to SentinAI (POST /api/v1/events).

Rules this module follows:
- A request is never slowed down. Records go into a small bounded queue and a
  background thread sends them in batches.
- A failed send is retried a few times with the same event_id, so the server
  never counts an event twice. If SentinAI stays down, events are dropped quietly
  and sending pauses for a minute. A 429 pauses for the time the server asks.
- Database exception messages are withheld, because they can carry names, phone
  numbers and emails. SentinAI masks other personal data on its side as well.
- Nothing happens unless SENTINAI_INGEST_URL and SENTINAI_INGEST_KEY are set.
"""

import logging
import os
import queue
import re
import threading
import time
import traceback
import uuid
from datetime import UTC, datetime

import requests

MAX_MESSAGE_CHARS = 1000
MAX_TRACE_CHARS = 6000
MAX_BATCH_EVENTS = 20
MAX_ATTEMPTS = 3
_EVENTS_PATH = "/api/v1/events"
_KEY_PREFIX = "snl_"
_ENV_NAME = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,31}$")

_LOCAL_PREFIXES = ("http://127.0.0.1", "http://localhost")
_DB_EXCEPTION = re.compile(r"^(sqlalchemy|psycopg2|psycopg|sqlite3|pymysql)[\w.]*:")
_TRACE_BOUNDARY = re.compile(
    r'^(Traceback \(|The above exception|During handling|\s+File ")'
)


def _safe_traceback(exc_info) -> str:
    """Format a traceback and cut the message of database exceptions."""
    text = "".join(traceback.format_exception(*exc_info))
    kept: list[str] = []
    skipping = False
    for line in text.splitlines():
        if _TRACE_BOUNDARY.match(line):
            skipping = False
        if skipping:
            continue
        if _DB_EXCEPTION.match(line):
            kept.append(line.split(":", 1)[0] + ": <message withheld>")
            skipping = True
            continue
        kept.append(line)
    return "\n".join(kept)


def _trim(text: str, limit: int) -> str:
    """Keep the start and the end (the exception line) inside the limit."""
    if len(text) <= limit:
        return text
    head = limit // 4
    return text[:head] + "\n  ... trimmed ...\n" + text[-(limit - head - 20):]


def _environment():
    """production on Render, else FLASK_ENV, else development. None if invalid."""
    if os.environ.get("RENDER"):
        name = "production"
    else:
        name = os.environ.get("FLASK_ENV", "").strip().lower() or "development"
    return name if _ENV_NAME.match(name) else None


def _release():
    return os.environ.get("RENDER_GIT_COMMIT", "").strip()[:64] or None


def _retry_after(response, default):
    try:
        value = float(response.headers.get("Retry-After", ""))
    except ValueError:
        return default
    return min(max(value, 1.0), 300.0)


class SentinAIHandler(logging.Handler):
    def __init__(
        self,
        url,
        key,
        *,
        flush_seconds=3.0,
        queue_size=200,
        timeout=3.0,
        pause_seconds=60.0,
        max_failures=3,
        max_attempts=MAX_ATTEMPTS,
        retry_delay=1.0,
    ):
        super().__init__(level=logging.ERROR)
        self._url = url
        self._key = key
        self._environment = _environment()
        self._release = _release()
        self._flush_seconds = flush_seconds
        self._queue_size = queue_size
        self._timeout = timeout
        self._pause_seconds = pause_seconds
        self._max_failures = max_failures
        self._max_attempts = max_attempts
        self._retry_delay = retry_delay
        self._queue = queue.Queue(maxsize=queue_size)
        self._thread = None
        self._pid = os.getpid()
        self._start_lock = threading.Lock()
        self._failures = 0
        self._paused_until = 0.0
        self.sent = 0
        self.dropped = 0

    def emit(self, record):
        # A logging handler must never raise into the application.
        try:
            if record.name.startswith(("urllib3", "requests")):
                return
            event = self._to_event(record)
            self._ensure_worker()
            self._queue.put_nowait(event)
        except Exception:
            self.dropped += 1

    def _to_event(self, record):
        message = (record.getMessage() or "").strip() or "(empty log message)"
        event = {
            "event_id": str(uuid.uuid4()),
            "message": message[:MAX_MESSAGE_CHARS],
            "level": "critical" if record.levelno >= logging.CRITICAL else "error",
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
        }
        if self._environment:
            event["environment"] = self._environment
        if self._release:
            event["release"] = self._release
        if record.exc_info and record.exc_info[0] is not None:
            event["exception_type"] = record.exc_info[0].__name__[:255]
            event["stacktrace"] = _trim(_safe_traceback(record.exc_info), MAX_TRACE_CHARS)
        return event

    def _ensure_worker(self):
        if self._worker_alive():
            return
        with self._start_lock:
            if self._worker_alive():
                return
            if self._pid != os.getpid():
                # Forked: the parent's queue and thread do not exist here.
                self._queue = queue.Queue(maxsize=self._queue_size)
                self._pid = os.getpid()
            thread = threading.Thread(
                target=self._run, name="sentinai-log-sender", daemon=True
            )
            thread.start()
            self._thread = thread

    def _worker_alive(self):
        return (
            self._thread is not None
            and self._pid == os.getpid()
            and self._thread.is_alive()
        )

    def _run(self):
        while True:
            batch = [self._queue.get()]
            deadline = time.monotonic() + self._flush_seconds
            while len(batch) < MAX_BATCH_EVENTS:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                try:
                    batch.append(self._queue.get(timeout=remaining))
                except queue.Empty:
                    break
            try:
                self._send(batch)
            except Exception:
                self.dropped += len(batch)

    def _pause(self, seconds=None):
        wait = self._pause_seconds if seconds is None else seconds
        self._paused_until = time.monotonic() + wait

    def _post(self, batch):
        """One attempt. Returns ok, retry, limited, unauthorized or rejected."""
        try:
            response = requests.post(
                self._url,
                json={"events": batch},
                headers={"Authorization": "Bearer " + self._key},
                timeout=self._timeout,
            )
        except requests.RequestException:
            return "retry"
        status = response.status_code
        if status < 300:
            return "ok"
        if status == 429:
            self._pause(_retry_after(response, self._pause_seconds))
            return "limited"
        if status in (401, 403):
            return "unauthorized"
        if status == 408 or status >= 500:
            return "retry"
        return "rejected"

    def _send(self, batch):
        if time.monotonic() < self._paused_until:
            self.dropped += len(batch)
            return
        outcome = "retry"
        for attempt in range(self._max_attempts):
            if attempt:
                time.sleep(self._retry_delay * attempt)
            outcome = self._post(batch)
            if outcome != "retry":
                break
        if outcome == "ok":
            self._failures = 0
            self.sent += len(batch)
            return
        self.dropped += len(batch)
        if outcome in ("rejected", "limited"):
            return
        self._failures += 1
        if self._failures >= self._max_failures:
            self._pause()
            self._failures = 0


def install(app):
    """Attach the handler to app.logger when SentinAI is configured."""
    url = os.environ.get("SENTINAI_INGEST_URL", "").strip()
    key = os.environ.get("SENTINAI_INGEST_KEY", "").strip()
    if not url or not key:
        return None
    if not url.startswith("https://") and not url.startswith(_LOCAL_PREFIXES):
        app.logger.warning("SENTINAI_INGEST_URL must use https, log forwarding is off")
        return None
    if not url.endswith(_EVENTS_PATH):
        app.logger.warning("SENTINAI_INGEST_URL must end with %s, forwarding is off", _EVENTS_PATH)
        return None
    if not key.startswith(_KEY_PREFIX):
        app.logger.warning("SENTINAI_INGEST_KEY must be a snl_ source key, forwarding is off")
        return None
    for existing in app.logger.handlers:
        if isinstance(existing, SentinAIHandler):
            return existing
    handler = SentinAIHandler(url, key)
    app.logger.addHandler(handler)
    return handler
