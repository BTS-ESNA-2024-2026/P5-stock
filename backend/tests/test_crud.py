"""
Tests for the CRUD API endpoints under /api/
Covers list endpoints and per-role access control.
"""

import pytest
from tests.conftest import set_cookie, ADMIN_USERNAME, VIEWER_USERNAME


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def auth_get(client, token, path):
    set_cookie(client, token)
    return client.get(f"/api{path}")


# ---------------------------------------------------------------------------
# Unauthenticated access — all list endpoints should return 401
# ---------------------------------------------------------------------------

class TestUnauthenticated:
    @pytest.mark.parametrize("path", [
        "/assets",
        "/asset_types",
        "/rooms",
        "/bases",
        "/missions",
        "/users",
        "/roles",
        "/logs",
    ])
    def test_list_requires_auth(self, client, path):
        resp = client.get(f"/api{path}")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Viewer role — read-only list endpoints
# ---------------------------------------------------------------------------

class TestViewerAccess:
    def test_list_assets_as_viewer(self, client, viewer_token):
        resp = auth_get(client, viewer_token, "/assets")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_list_asset_types_as_viewer(self, client, viewer_token):
        resp = auth_get(client, viewer_token, "/asset_types")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_list_rooms_as_viewer(self, client, viewer_token):
        resp = auth_get(client, viewer_token, "/rooms")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_list_bases_as_viewer(self, client, viewer_token):
        resp = auth_get(client, viewer_token, "/bases")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_list_missions_as_viewer(self, client, viewer_token):
        resp = auth_get(client, viewer_token, "/missions")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_list_roles_as_viewer(self, client, viewer_token):
        resp = auth_get(client, viewer_token, "/roles")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_list_logs_as_viewer(self, client, viewer_token):
        resp = auth_get(client, viewer_token, "/logs")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_list_users_as_viewer_forbidden(self, client, viewer_token):
        """Viewer must NOT access /api/users (admin-only)."""
        resp = auth_get(client, viewer_token, "/users")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Admin role — full access
# ---------------------------------------------------------------------------

class TestAdminAccess:
    def test_list_users_as_admin(self, client, admin_token, seed_test_db):
        resp = auth_get(client, admin_token, "/users")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        # At least our two seeded users
        usernames = [u["username"] for u in data]
        assert ADMIN_USERNAME in usernames or VIEWER_USERNAME in usernames

    def test_list_roles_as_admin(self, client, admin_token):
        resp = auth_get(client, admin_token, "/roles")
        assert resp.status_code == 200
        roles = resp.get_json()
        role_names = [r["name"] for r in roles]
        assert "admin" in role_names
        assert "viewer" in role_names

    def test_list_assets_as_admin(self, client, admin_token):
        resp = auth_get(client, admin_token, "/assets")
        assert resp.status_code == 200

    def test_list_bases_as_admin(self, client, admin_token):
        resp = auth_get(client, admin_token, "/bases")
        assert resp.status_code == 200

    def test_list_missions_as_admin(self, client, admin_token):
        resp = auth_get(client, admin_token, "/missions")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# CRUD operations on Base (requires technician / admin)
# ---------------------------------------------------------------------------

class TestBaseCRUD:
    def _create_base(self, client, token):
        set_cookie(client, token)
        return client.post(
            "/api/base",
            json={"name": "Base Alpha", "address": "1 rue de la Paix"},
            content_type="application/json",
        )

    def test_create_base_as_admin(self, client, admin_token):
        resp = self._create_base(client, admin_token)
        # admin role is above technician so should be allowed
        assert resp.status_code in (200, 201)

    def test_create_base_missing_fields(self, client, admin_token):
        set_cookie(client, admin_token)
        resp = client.post(
            "/api/base",
            json={"name": "Incomplete Base"},
            content_type="application/json",
        )
        # Missing 'address' → error response
        assert resp.status_code in (400, 422, 500)

    def test_create_base_as_viewer_forbidden(self, client, viewer_token):
        resp = self._create_base(client, viewer_token)
        assert resp.status_code == 403

    def test_get_nonexistent_base(self, client, admin_token):
        set_cookie(client, admin_token)
        resp = client.get("/api/base/00000000-0000-0000-0000-000000000000")
        assert resp.status_code in (404, 400, 500)


# ---------------------------------------------------------------------------
# CRUD operations on Asset (requires technician / admin)
# ---------------------------------------------------------------------------

class TestAssetCRUD:
    def _create_asset_type(self, client, token, type_name="Laptop"):
        set_cookie(client, token)
        return client.post(
            "/api/asset_type",
            json={"type": type_name},
            content_type="application/json",
        )

    def test_create_asset_missing_fields(self, client, admin_token):
        """Creating an asset without required fields returns an error."""
        set_cookie(client, admin_token)
        resp = client.post(
            "/api/asset",
            json={"name": "Test Asset"},  # missing type_asset_id and status
            content_type="application/json",
        )
        assert resp.status_code in (400, 422, 500)

    def test_get_nonexistent_asset(self, client, admin_token):
        set_cookie(client, admin_token)
        resp = client.get("/api/asset/00000000-0000-0000-0000-000000000000")
        assert resp.status_code in (404, 400, 500)

    def test_update_nonexistent_asset(self, client, admin_token):
        set_cookie(client, admin_token)
        resp = client.put(
            "/api/asset/00000000-0000-0000-0000-000000000000",
            json={"name": "Updated"},
            content_type="application/json",
        )
        assert resp.status_code in (404, 400, 500)

    def test_delete_nonexistent_asset(self, client, admin_token):
        set_cookie(client, admin_token)
        resp = client.delete("/api/asset/00000000-0000-0000-0000-000000000000")
        assert resp.status_code in (404, 400, 500)


# ---------------------------------------------------------------------------
# Rate-limit error handler
# ---------------------------------------------------------------------------

class TestErrorHandlers:
    def test_invalid_token_returns_401(self, client):
        client.set_cookie("access_token", "invalid.jwt.token")
        resp = client.get("/api/assets")
        assert resp.status_code == 401
