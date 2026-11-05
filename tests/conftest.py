import os
import tempfile

import pytest

# Set before app is imported. Empty strings (not removed) so load_dotenv()
# on a developer machine cannot fill them in from a local .env file.
_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = "sqlite:///" + _db.name
for _name in ("SENTINAI_INGEST_URL", "SENTINAI_INGEST_KEY", "SUPABASE_URL"):
    os.environ[_name] = ""

import app as m  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with m.app.app_context():
        m.db.create_all()
    return m.app.test_client()


import pytest as _pytest


@_pytest.fixture(autouse=True)
def _csrf_off_by_default():
    import app as appmod
    appmod.app.config["WTF_CSRF_ENABLED"] = False
    yield
    appmod.app.config["WTF_CSRF_ENABLED"] = True
