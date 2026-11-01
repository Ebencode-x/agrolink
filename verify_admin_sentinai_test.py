"""Check POST /admin/sentinai-test: admin only, and it raises a logged 500.

Run:  venv/bin/python verify_admin_sentinai_test.py
Nothing is sent to SentinAI.
"""

import logging
import sys

from app import User, app

failures = []


def check(label, condition):
    print(("[OK] " if condition else "[FAIL] ") + label)
    if not condition:
        failures.append(label)


class Capture(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.ERROR)
        self.records = []

    def emit(self, record):
        self.records.append(record)


with app.app_context():
    admin = User.query.filter_by(role="admin").first()
    other = User.query.filter(User.role != "admin").first()
    admin_id = admin.id if admin else None
    other_id = other.id if other else None

if admin_id is None:
    print("[SKIP] No admin user in the database.")
    sys.exit(0)

capture = Capture()
app.logger.addHandler(capture)


def client_for(user_id):
    client = app.test_client()
    if user_id is not None:
        with client.session_transaction() as sess:
            sess["_user_id"] = str(user_id)
            sess["_fresh"] = True
    return client


URL = "/admin/sentinai-test"

response = client_for(None).post(URL)
check("anonymous is sent to login, not served", response.status_code in (301, 302, 401))
check("anonymous causes no error log", not capture.records)

if other_id is not None:
    response = client_for(other_id).post(URL)
    check("a non-admin gets 403", response.status_code == 403)
    check("a non-admin causes no error log", not capture.records)
else:
    print("[SKIP] No non-admin user to test with.")

response = client_for(admin_id).get(URL)
check("GET is not allowed (405)", response.status_code == 405)

response = client_for(admin_id).post(URL)
check("admin POST returns the 500 page", response.status_code == 500)
check(
    "the RuntimeError was logged with its traceback",
    any(r.exc_info and r.exc_info[0] is RuntimeError for r in capture.records),
)

if failures:
    print(f"[RESULT] {len(failures)} check(s) failed")
    sys.exit(1)
print("[RESULT] all checks passed")
