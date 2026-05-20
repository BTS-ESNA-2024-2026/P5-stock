"""
Tests for the authentication routes:
  POST /auth/login
  POST /auth/register
  GET  /auth/me
  POST /auth/logout
  POST /auth/otp/setup
  DELETE /auth/otp/setup
"""

import pytest
from tests.conftest import TEST_PASSWORD, ADMIN_USERNAME, VIEWER_USERNAME, set_cookie


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

class TestLogin:
    def test_login_success(self, client, seed_test_db):
        """Valid credentials return 200 and set the access_token cookie."""
        resp = client.post(
            "/auth/login",
            data={"username": ADMIN_USERNAME, "password": TEST_PASSWORD},
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["message"] == "Login successful"
        assert "access_token" in resp.headers.get("Set-Cookie", "")

    def test_login_wrong_password(self, client, seed_test_db):
        """Wrong password returns 401."""
        resp = client.post(
            "/auth/login",
            data={"username": ADMIN_USERNAME, "password": "wrongpassword"},
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 401
        assert "incorrect" in resp.get_json()["message"].lower()

    def test_login_unknown_user(self, client, seed_test_db):
        """Non-existent username returns 401."""
        resp = client.post(
            "/auth/login",
            data={"username": "nobody", "password": TEST_PASSWORD},
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 401

    def test_login_missing_username(self, client):
        """Missing username field returns 401."""
        resp = client.post(
            "/auth/login",
            data={"password": TEST_PASSWORD},
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 401

    def test_login_missing_password(self, client, seed_test_db):
        """Missing password field returns 401."""
        resp = client.post(
            "/auth/login",
            data={"username": ADMIN_USERNAME},
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 401

    def test_login_empty_body(self, client):
        """Empty body returns 401."""
        resp = client.post(
            "/auth/login",
            data={},
            content_type="application/x-www-form-urlencoded",
        )
        assert resp.status_code == 401

    def test_login_redirect_get(self, client):
        """GET /auth/login redirects to the frontend login page."""
        resp = client.get("/auth/login")
        assert resp.status_code == 302
        assert "login" in resp.headers["Location"]


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------

class TestRegister:
    """Self-registration is intentionally disabled (UC-02 says only admins
    create accounts, via POST /api/user). The endpoint must return 410 Gone
    regardless of payload to keep historic links explicit, not silent."""

    def test_register_disabled(self, client):
        resp = client.post(
            "/auth/register",
            json={"username": "newuser42", "password": "SecurePass!9999"},
        )
        assert resp.status_code == 410
        assert "disabled" in resp.get_json()["message"].lower()

    def test_register_disabled_even_with_no_body(self, client):
        resp = client.post("/auth/register")
        assert resp.status_code == 410

    def test_register_disabled_with_existing_username(self, client, seed_test_db):
        resp = client.post(
            "/auth/register",
            json={"username": ADMIN_USERNAME, "password": "SomePass!1234"},
        )
        assert resp.status_code == 410


# ---------------------------------------------------------------------------
# GET /auth/me
# ---------------------------------------------------------------------------

class TestGetMe:
    def test_me_authenticated(self, client, admin_token):
        """Authenticated user receives their profile."""
        set_cookie(client, admin_token)
        resp = client.get("/auth/me")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["username"] == ADMIN_USERNAME
        assert "id" in data
        assert "role" in data

    def test_me_viewer_authenticated(self, client, viewer_token):
        """Viewer user can also access /auth/me."""
        set_cookie(client, viewer_token)
        resp = client.get("/auth/me")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["username"] == VIEWER_USERNAME

    def test_me_unauthenticated(self, client):
        """No cookie → 401."""
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    def test_me_invalid_token(self, client):
        """Garbage token → 401."""
        client.set_cookie("access_token", "this.is.not.a.valid.jwt")
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    def test_me_expired_token(self, client, app, rsa_private_key, seed_test_db):
        """Expired JWT → 401."""
        from src.database.model import User
        from tests.conftest import make_token

        with app.app_context():
            user = app.extensions["sqlalchemy"].session.query(User).filter_by(
                username=ADMIN_USERNAME
            ).first()
            expired = make_token(str(user.id), rsa_private_key, expired=True)

        client.set_cookie("access_token", expired)
        resp = client.get("/auth/me")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /auth/logout
# ---------------------------------------------------------------------------

class TestLogout:
    def test_logout_clears_cookie(self, client, admin_token):
        """Logout responds 200 and deletes the access_token cookie."""
        set_cookie(client, admin_token)
        resp = client.post("/auth/logout")
        assert resp.status_code == 200
        # Cookie should be expired/deleted (Max-Age=0 or explicit delete)
        cookie_header = resp.headers.get("Set-Cookie", "")
        assert "access_token" in cookie_header

    def test_logout_unauthenticated_still_200(self, client):
        """Logout without a session still returns 200 (idempotent)."""
        resp = client.post("/auth/logout")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /auth/otp/setup  /  DELETE /auth/otp/setup
# ---------------------------------------------------------------------------

class TestOtpSetup:
    def test_otp_setup_authenticated(self, client, admin_token):
        """Admin can set up OTP and receives a secret + URI."""
        set_cookie(client, admin_token)
        resp = client.post("/auth/otp/setup")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "secret" in data
        assert "uri" in data

    def test_otp_setup_unauthenticated(self, client):
        """OTP setup without auth → 401."""
        resp = client.post("/auth/otp/setup")
        assert resp.status_code == 401

    def test_otp_delete_authenticated(self, client, app, rsa_private_key, seed_test_db):
        """Admin can disable OTP."""
        from src.database.model import User
        from tests.conftest import make_token

        with app.app_context():
            user = app.extensions["sqlalchemy"].session.query(User).filter_by(
                username=ADMIN_USERNAME
            ).first()
            token = make_token(str(user.id), rsa_private_key)

        client.set_cookie("access_token", token)
        resp = client.delete("/auth/otp/setup")
        assert resp.status_code == 200

    def test_otp_delete_unauthenticated(self, client):
        """OTP delete without auth → 401."""
        resp = client.delete("/auth/otp/setup")
        assert resp.status_code == 401
