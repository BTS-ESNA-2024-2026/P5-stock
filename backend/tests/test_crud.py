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


# ---------------------------------------------------------------------------
# /api/specs list endpoint
# ---------------------------------------------------------------------------

class TestSpecsEndpoint:
    def test_list_specs_unauthenticated(self, client):
        resp = client.get("/api/specs")
        assert resp.status_code == 401

    def test_list_specs_as_viewer(self, client, viewer_token):
        set_cookie(client, viewer_token)
        resp = client.get("/api/specs")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_list_specs_as_admin(self, client, admin_token):
        set_cookie(client, admin_token)
        resp = client.get("/api/specs")
        assert resp.status_code == 200

    def test_create_spec_as_viewer_forbidden(self, client, viewer_token):
        set_cookie(client, viewer_token)
        resp = client.post(
            "/api/spec",
            json={"type_id": "00000000-0000-0000-0000-000000000001", "name": "Kilometrage"},
            content_type="application/json",
        )
        assert resp.status_code == 403

    def test_create_spec_missing_fields(self, client, admin_token):
        set_cookie(client, admin_token)
        resp = client.post(
            "/api/spec",
            json={"name": "Kilometrage"},  # missing type_id
            content_type="application/json",
        )
        assert resp.status_code in (400, 422, 500)


# ---------------------------------------------------------------------------
# /api/asset/<id>/values endpoint
# ---------------------------------------------------------------------------

class TestAssetValues:
    def _create_full_asset(self, client, admin_token):
        """Creates an asset type, then an asset; returns (type_id, asset_id)."""
        set_cookie(client, admin_token)

        # Create asset type and retrieve its id from the list
        r = client.post(
            "/api/asset_type",
            json={"type": "Vehicule_test"},
            content_type="application/json",
        )
        assert r.status_code in (200, 201)

        r = client.get("/api/asset_types")
        assert r.status_code == 200
        types = r.get_json()
        type_id = next(t["id"] for t in types if t["type"] == "Vehicule_test")

        # Create asset and retrieve its id from the list
        r = client.post(
            "/api/asset",
            json={"type_asset_id": type_id, "name": "Camion_test", "status": "STOCK"},
            content_type="application/json",
        )
        assert r.status_code in (200, 201)

        r = client.get("/api/assets")
        assert r.status_code == 200
        assets = r.get_json()
        asset_id = next(a["id"] for a in assets if a["name"] == "Camion_test")
        return type_id, asset_id

    def test_list_values_unauthenticated(self, client):
        resp = client.get("/api/asset/00000000-0000-0000-0000-000000000000/values")
        assert resp.status_code == 401

    def test_list_values_nonexistent_asset(self, client, viewer_token):
        set_cookie(client, viewer_token)
        resp = client.get("/api/asset/00000000-0000-0000-0000-000000000000/values")
        assert resp.status_code in (404, 400, 500)

    def test_list_values_as_viewer(self, client, admin_token, viewer_token):
        _, asset_id = self._create_full_asset(client, admin_token)
        set_cookie(client, viewer_token)
        resp = client.get(f"/api/asset/{asset_id}/values")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_create_and_list_value(self, client, admin_token):
        """Create an asset_type, spec, asset, value; verify it appears in /values."""
        type_id, asset_id = self._create_full_asset(client, admin_token)

        set_cookie(client, admin_token)
        r = client.post(
            "/api/spec",
            json={"type_id": type_id, "name": "Kilometrage_list"},
            content_type="application/json",
        )
        assert r.status_code in (200, 201)

        # Retrieve spec id from list
        r = client.get("/api/specs")
        specs = r.get_json()
        spec_id = next(s["id"] for s in specs if s["name"] == "Kilometrage_list")

        # Create value
        r = client.post(
            "/api/value",
            json={"asset_id": asset_id, "spec_id": spec_id, "value": "25000 km"},
            content_type="application/json",
        )
        assert r.status_code in (200, 201)

        # List values for asset
        r = client.get(f"/api/asset/{asset_id}/values")
        assert r.status_code == 200
        values = r.get_json()
        assert any(v["spec_id"] == spec_id and v["value"] == "25000 km" for v in values)
        # spec_name should be joined
        matching = next(v for v in values if v["spec_id"] == spec_id)
        assert matching["spec_name"] == "Kilometrage_list"

    def test_create_value_as_viewer_forbidden(self, client, admin_token, viewer_token):
        _, asset_id = self._create_full_asset(client, admin_token)
        set_cookie(client, viewer_token)
        resp = client.post(
            "/api/value",
            json={"asset_id": asset_id, "spec_id": "00000000-0000-0000-0000-000000000001", "value": "42"},
            content_type="application/json",
        )
        assert resp.status_code == 403

    def test_update_value(self, client, admin_token):
        type_id, asset_id = self._create_full_asset(client, admin_token)

        set_cookie(client, admin_token)
        r = client.post("/api/spec", json={"type_id": type_id, "name": "Poids_upd"}, content_type="application/json")
        assert r.status_code in (200, 201)

        r = client.get("/api/specs")
        specs = r.get_json()
        spec_id = next(s["id"] for s in specs if s["name"] == "Poids_upd")

        r = client.post("/api/value", json={"asset_id": asset_id, "spec_id": spec_id, "value": "5T"}, content_type="application/json")
        assert r.status_code in (200, 201)

        r = client.get(f"/api/asset/{asset_id}/values")
        values = r.get_json()
        value_id = next(v["id"] for v in values if v["spec_id"] == spec_id)

        r = client.put(f"/api/value/{value_id}", json={"value": "6T"}, content_type="application/json")
        assert r.status_code in (200, 201)

        r = client.get(f"/api/asset/{asset_id}/values")
        values = r.get_json()
        matching = next(v for v in values if v["id"] == value_id)
        assert matching["value"] == "6T"

    def test_delete_value(self, client, admin_token):
        type_id, asset_id = self._create_full_asset(client, admin_token)

        set_cookie(client, admin_token)
        r = client.post("/api/spec", json={"type_id": type_id, "name": "Couleur_del"}, content_type="application/json")
        assert r.status_code in (200, 201)

        r = client.get("/api/specs")
        specs = r.get_json()
        spec_id = next(s["id"] for s in specs if s["name"] == "Couleur_del")

        r = client.post("/api/value", json={"asset_id": asset_id, "spec_id": spec_id, "value": "Rouge"}, content_type="application/json")
        assert r.status_code in (200, 201)

        r = client.get(f"/api/asset/{asset_id}/values")
        values = r.get_json()
        value_id = next(v["id"] for v in values if v["spec_id"] == spec_id)

        r = client.delete(f"/api/value/{value_id}")
        assert r.status_code in (200, 201)

        r = client.get(f"/api/asset/{asset_id}/values")
        values = r.get_json()
        assert not any(v["id"] == value_id for v in values)


# ---------------------------------------------------------------------------
# Full CRUD on AssetType
# ---------------------------------------------------------------------------

class TestAssetTypeCRUD:
    def test_create_asset_type_as_admin(self, client, admin_token):
        set_cookie(client, admin_token)
        r = client.post("/api/asset_type", json={"type": "Armement"}, content_type="application/json")
        assert r.status_code in (200, 201)
        data = r.get_json()
        assert data.get("status") == "success"

    def test_create_asset_type_as_viewer_forbidden(self, client, viewer_token):
        set_cookie(client, viewer_token)
        r = client.post("/api/asset_type", json={"type": "MRE"}, content_type="application/json")
        assert r.status_code == 403

    def test_create_asset_type_missing_field(self, client, admin_token):
        set_cookie(client, admin_token)
        r = client.post("/api/asset_type", json={}, content_type="application/json")
        assert r.status_code in (400, 422, 500)

    def test_get_asset_type(self, client, admin_token):
        set_cookie(client, admin_token)
        r = client.post("/api/asset_type", json={"type": "Equipement_get"}, content_type="application/json")
        assert r.status_code in (200, 201)

        r = client.get("/api/asset_types")
        types = r.get_json()
        type_id = next(t["id"] for t in types if t["type"] == "Equipement_get")

        r = client.get(f"/api/asset_type/{type_id}")
        assert r.status_code in (200, 201)

    def test_update_asset_type(self, client, admin_token):
        set_cookie(client, admin_token)
        r = client.post("/api/asset_type", json={"type": "Vehicule_v1_upd"}, content_type="application/json")
        assert r.status_code in (200, 201)

        r = client.get("/api/asset_types")
        types = r.get_json()
        type_id = next(t["id"] for t in types if t["type"] == "Vehicule_v1_upd")

        r = client.put(f"/api/asset_type/{type_id}", json={"type": "Vehicule_v2_upd"}, content_type="application/json")
        assert r.status_code in (200, 201)

    def test_delete_asset_type(self, client, admin_token):
        set_cookie(client, admin_token)
        r = client.post("/api/asset_type", json={"type": "ToDelete_type"}, content_type="application/json")
        assert r.status_code in (200, 201)

        r = client.get("/api/asset_types")
        types = r.get_json()
        type_id = next(t["id"] for t in types if t["type"] == "ToDelete_type")

        r = client.delete(f"/api/asset_type/{type_id}")
        assert r.status_code in (200, 201)


# ---------------------------------------------------------------------------
# Full CRUD on Base
# ---------------------------------------------------------------------------

class TestBaseCRUDFull:
    def test_create_get_update_delete_base(self, client, admin_token):
        set_cookie(client, admin_token)

        # Create
        r = client.post("/api/base", json={"name": "Base Bravo_full", "address": "Marseille"}, content_type="application/json")
        assert r.status_code in (200, 201)

        # Get id from list
        r = client.get("/api/bases")
        bases = r.get_json()
        base_id = next(b["id"] for b in bases if b["name"] == "Base Bravo_full")

        # Get
        r = client.get(f"/api/base/{base_id}")
        assert r.status_code in (200, 201)

        # Update
        r = client.put(f"/api/base/{base_id}", json={"name": "Base Bravo_full 2", "address": "Lyon"}, content_type="application/json")
        assert r.status_code in (200, 201)

        # Appears in list
        r = client.get("/api/bases")
        bases = r.get_json()
        assert any(b["id"] == base_id for b in bases)

        # Delete
        r = client.delete(f"/api/base/{base_id}")
        assert r.status_code in (200, 201)
