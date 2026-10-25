"""Forward ERROR level log records to SentinAI (POST /api/ingest).

Rules this module follows:
- A request is never slowed down. Records go into a small bounded queue and a
  background thread sends them in batches.
- If SentinAI is asleep or down, events are dropped quietly and sending pauses
  for a minute after repeated failures.
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

import requests

MAX_MESSAGE_CHARS = 1000
MAX_TRACE_CHARS = 6000
MAX_BATCH_EVENTS = 20

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


class SentinAIHandler(logging.Handler):
    def __init__(
        self,
        url,
        key,
        *,
        source="agrolink",
        flush_seconds=3.0,
        queue_size=200,
        timeout=3.0,
        pause_seconds=60.0,
        max_failures=3,
    ):
        super().__init__(level=logging.ERROR)
        self._url = url
        self._key = key
        self._source = source
        self._flush_seconds = flush_seconds
        self._queue_size = queue_size
        self._timeout = timeout
        self._pause_seconds = pause_seconds
        self._max_failures = max_failures
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

    @staticmethod
    def _to_event(record):
        message = (record.getMessage() or "").strip() or "(empty log message)"
        event = {"message": message[:MAX_MESSAGE_CHARS]}
        if record.exc_info and record.exc_info[0] is not None:
            event["traceback"] = _trim(_safe_traceback(record.exc_info), MAX_TRACE_CHARS)
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

    def _send(self, batch):
        if time.monotonic() < self._paused_until:
            self.dropped += len(batch)
            return
        try:
            response = requests.post(
                self._url,
                json={"source": self._source, "events": batch},
                headers={"X-Ingest-Key": self._key},
                timeout=self._timeout,
            )
            ok = response.status_code < 300
            if response.status_code == 429:
                self._paused_until = time.monotonic() + self._pause_seconds
        except requests.RequestException:
            ok = False
        if ok:
            self._failures = 0
            self.sent += len(batch)
            return
        self.dropped += len(batch)
        self._failures += 1
        if self._failures >= self._max_failures:
            self._paused_until = time.monotonic() + self._pause_seconds
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
    for existing in app.logger.handlers:
        if isinstance(existing, SentinAIHandler):
            return existing
    handler = SentinAIHandler(url, key)
    app.logger.addHandler(handler)
    return handler
