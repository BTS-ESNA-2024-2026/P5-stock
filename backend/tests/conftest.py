"""
Pytest configuration and shared fixtures for the P5-stock backend tests.

Local runs: uses SQLite in-memory (DATABASE_URL defaults to sqlite:///:memory:).
            SEED_SQL is patched to a no-op to avoid PostgreSQL-specific syntax.
CI runs:    uses a real PostgreSQL service container via DATABASE_URL env var.
            SEED_SQL runs as-is against PostgreSQL.

A session-scoped RSA key pair is generated so tests never need pre-existing PEM files.
"""

import os
import tempfile
import pytest
from datetime import datetime, timedelta, UTC
from uuid import UUID

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# ---------------------------------------------------------------------------
# Environment — set BEFORE the application modules are imported so that
# Flask / SQLAlchemy pick up the test values.
# ---------------------------------------------------------------------------
if os.environ.get("CI") == "true":
    # CI: DATABASE_URL is set by the workflow (PostgreSQL service container).
    # We use it as-is.  The variable must be present; fail loudly if not.
    if not os.environ.get("DATABASE_URL"):
        raise RuntimeError("CI=true but DATABASE_URL is not set.")
else:
    # Local development: always create a fresh SQLite temp file so that
    # tests never touch the dev/prod PostgreSQL database and each run
    # starts with a clean state.
    _tmp_db_fd, _tmp_db_path = tempfile.mkstemp(suffix=".db", prefix="p5test_")
    os.close(_tmp_db_fd)
    os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db_path}"
os.environ.setdefault("FLASK_SECRET_KEY", "test-secret-key-do-not-use-in-prod")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")


# ---------------------------------------------------------------------------
# Session-scoped RSA key pair
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def rsa_private_key():
    """Generate a fresh RSA-2048 key pair once per test session."""
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )


@pytest.fixture(scope="session", autouse=True)
def rsa_key_files(tmp_path_factory, rsa_private_key):
    """
    Write PEM files into a temp directory and change the working directory to
    that folder for the duration of the session.  This satisfies the ``open(
    'private.pem', ...)`` calls inside the auth routes.
    """
    key_dir = tmp_path_factory.mktemp("keys")

    private_pem = rsa_private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = rsa_private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    (key_dir / "private.pem").write_bytes(private_pem)
    (key_dir / "public.pem").write_bytes(public_pem)

    original_cwd = os.getcwd()
    os.chdir(key_dir)
    yield key_dir
    os.chdir(original_cwd)


# ---------------------------------------------------------------------------
# Flask application
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def app(rsa_key_files):
    """
    Create the Flask application configured for testing:
      - SQLite in-memory database (local) or PostgreSQL (CI via DATABASE_URL)
      - SEED_SQL patched to no-op when using SQLite (avoids PG-specific syntax)
      - Rate-limiting disabled
    """
    import src
    from src.services.config import limiter

    db_url = os.environ.get("DATABASE_URL", "")
    using_sqlite = db_url.startswith("sqlite")

    if using_sqlite:
        # src.SEED_SQL is the local name imported by `from src.database.init_db import SEED_SQL`
        # in src/__init__.py — create_app() reads THIS name, not init_db.SEED_SQL.
        original_seed = src.SEED_SQL
        src.SEED_SQL = "SELECT 1"

    application = src.create_app()
    application.config["TESTING"] = True
    application.config["WTF_CSRF_ENABLED"] = False

    # Disable rate limiting for tests.
    # Flask-Limiter 3.7+ caches `self.enabled` at init_app time, so we must
    # also flip the instance attribute directly; changing app.config alone is
    # not enough.
    application.config["RATELIMIT_ENABLED"] = False
    limiter.enabled = False

    if using_sqlite:
        src.SEED_SQL = original_seed  # restore

    yield application


@pytest.fixture
def client(app):
    """Return a fresh test client for each test."""
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Database seed helpers
# ---------------------------------------------------------------------------

ADMIN_ROLE_ID  = UUID("019563a0-0000-7000-8000-000000000001")
VIEWER_ROLE_ID = UUID("019563a0-0000-7000-8000-000000000005")

ADMIN_USERNAME  = "test_admin"
VIEWER_USERNAME = "test_viewer"
TEST_PASSWORD   = "TestPassword123!"


@pytest.fixture(scope="session", autouse=True)
def seed_test_db(app):
    """
    Insert the minimum set of roles and users needed by the test suite.
    Runs once per session inside an app context.
    """
    from src.database.model import db, Role, User, ph

    with app.app_context():
        # Roles
        for role_id, name, perms in [
            (ADMIN_ROLE_ID, "admin",
             {"manage_admins": True, "admin_panel": True,
              "sensible_access": True, "edit_assets": True, "view_assets": True}),
            (UUID("019563a0-0000-7000-8000-000000000002"), "technician",
             {"manage_admins": False, "admin_panel": True,
              "sensible_access": True, "edit_assets": True, "view_assets": True}),
            (UUID("019563a0-0000-7000-8000-000000000003"), "secure_user",
             {"manage_admins": False, "admin_panel": False,
              "sensible_access": True, "edit_assets": True, "view_assets": True}),
            (UUID("019563a0-0000-7000-8000-000000000004"), "user",
             {"manage_admins": False, "admin_panel": False,
              "sensible_access": False, "edit_assets": True, "view_assets": True}),
            (VIEWER_ROLE_ID, "viewer",
             {"manage_admins": False, "admin_panel": False,
              "sensible_access": False, "edit_assets": False, "view_assets": True}),
        ]:
            if not db.session.get(Role, role_id):
                role = Role()
                role.id    = role_id
                role.name  = name
                role.perms = perms
                db.session.add(role)

        # Users
        for username, role_id in [
            (ADMIN_USERNAME,  ADMIN_ROLE_ID),
            (VIEWER_USERNAME, VIEWER_ROLE_ID),
        ]:
            if not db.session.query(User).filter_by(username=username).first():
                user = User(
                    username=username,
                    group_id=role_id,
                    hash=ph.hash(TEST_PASSWORD),
                    hash_algorithm="argon2",
                )
                db.session.add(user)

        db.session.commit()


# ---------------------------------------------------------------------------
# JWT token helper
# ---------------------------------------------------------------------------

def make_token(user_id: str, private_key, expired: bool = False) -> str:
    """Create a signed RS256 JWT for the given user_id."""
    import jwt as pyjwt
    from src.services.crypto import JWT_AUDIENCE, JWT_ISSUER

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    delta = timedelta(hours=-1) if expired else timedelta(hours=1)
    payload = {
        "user_id": user_id,
        "exp": datetime.now(UTC) + delta,
        "iat": datetime.now(UTC),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "type": "access",
    }
    return pyjwt.encode(payload, private_pem, algorithm="RS256")


@pytest.fixture
def admin_token(app, rsa_private_key, seed_test_db):
    """Return a valid JWT cookie value for the admin user."""
    from src.database.model import User

    with app.app_context():
        user = app.extensions["sqlalchemy"].session.query(User).filter_by(
            username=ADMIN_USERNAME
        ).first()
        return make_token(str(user.id), rsa_private_key)


@pytest.fixture
def viewer_token(app, rsa_private_key, seed_test_db):
    """Return a valid JWT cookie value for the viewer user."""
    from src.database.model import User

    with app.app_context():
        user = app.extensions["sqlalchemy"].session.query(User).filter_by(
            username=VIEWER_USERNAME
        ).first()
        return make_token(str(user.id), rsa_private_key)


def set_cookie(client, token: str):
    """Helper – attach an access_token cookie to the test client."""
    client.set_cookie("access_token", token)
