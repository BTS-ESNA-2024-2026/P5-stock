"""
Unit tests for service-layer helpers:
  - validate_username
  - verify_password
  - _serialize_value (from CRUD_tools)
"""

import pytest
from datetime import datetime
from uuid import UUID


# ---------------------------------------------------------------------------
# validate_username
# ---------------------------------------------------------------------------

class TestValidateUsername:
    def setup_method(self):
        from src.services.tools import validate_username
        self.validate = validate_username

    def test_valid_simple(self):
        assert self.validate("alice") is True

    def test_valid_with_underscore(self):
        assert self.validate("alice_bob") is True

    def test_valid_with_hyphen(self):
        assert self.validate("alice-bob") is True

    def test_valid_alphanumeric(self):
        assert self.validate("User123") is True

    def test_valid_max_length(self):
        assert self.validate("a" * 35) is True

    def test_too_short_single_char(self):
        assert self.validate("a") is False

    def test_too_short_empty(self):
        assert self.validate("") is False

    def test_too_long(self):
        assert self.validate("a" * 36) is False

    def test_forbidden_word_admin(self):
        assert self.validate("admin") is False

    def test_forbidden_word_root(self):
        assert self.validate("root") is False

    def test_forbidden_word_system(self):
        assert self.validate("system") is False

    def test_forbidden_word_null(self):
        assert self.validate("null") is False

    def test_forbidden_word_select(self):
        assert self.validate("select") is False

    def test_forbidden_word_drop(self):
        assert self.validate("drop") is False

    def test_forbidden_word_insert(self):
        assert self.validate("insert") is False

    def test_forbidden_word_undefined(self):
        assert self.validate("undefined") is False

    def test_special_chars_space(self):
        assert self.validate("bad user") is False

    def test_special_chars_exclamation(self):
        assert self.validate("bad!user") is False

    def test_special_chars_at(self):
        assert self.validate("bad@user") is False

    def test_special_chars_dot(self):
        assert self.validate("bad.user") is False

    def test_case_insensitive_forbidden(self):
        # 'ADMIN' should also be forbidden (lower() check)
        assert self.validate("ADMIN") is False


# ---------------------------------------------------------------------------
# verify_password
# ---------------------------------------------------------------------------

class TestVerifyPassword:
    def setup_method(self):
        from src.services.tools import verify_password
        from src.database.model import ph
        self.verify = verify_password
        self.ph = ph

    def test_correct_password(self):
        hashed = self.ph.hash("correct_password")
        assert self.verify("correct_password", hashed) is True

    def test_wrong_password(self):
        hashed = self.ph.hash("correct_password")
        assert self.verify("wrong_password", hashed) is False

    def test_empty_vs_non_empty(self):
        hashed = self.ph.hash("some_password")
        assert self.verify("", hashed) is False

    def test_case_sensitive(self):
        hashed = self.ph.hash("Password")
        assert self.verify("password", hashed) is False


# ---------------------------------------------------------------------------
# _serialize_value
# ---------------------------------------------------------------------------

class TestSerializeValue:
    def setup_method(self):
        from src.services.CRUD_tools import _serialize_value
        self.serialize = _serialize_value

    def test_uuid_becomes_string(self):
        uid = UUID("12345678-1234-5678-1234-567812345678")
        result = self.serialize(uid)
        assert isinstance(result, str)
        assert result == "12345678-1234-5678-1234-567812345678"

    def test_datetime_becomes_isoformat(self):
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = self.serialize(dt)
        assert isinstance(result, str)
        assert "2024-01-15" in result

    def test_string_passthrough(self):
        assert self.serialize("hello") == "hello"

    def test_int_passthrough(self):
        assert self.serialize(42) == 42

    def test_bool_passthrough(self):
        assert self.serialize(True) is True

    def test_none_passthrough(self):
        assert self.serialize(None) is None

    def test_list_passthrough(self):
        lst = [1, 2, 3]
        assert self.serialize(lst) == lst

    def test_dict_passthrough(self):
        d = {"key": "value"}
        assert self.serialize(d) == d


# ---------------------------------------------------------------------------
# jwt_decode (unit-level, no DB)
# ---------------------------------------------------------------------------

class TestJwtDecode:
    """
    jwt_decode reads the public key from 'public.pem' and queries the DB.
    These tests only verify the token-validation logic; the rsa_key_files
    session fixture ensures the PEM files are present.
    """

    def test_no_cookie_returns_false(self, app):
        with app.test_request_context("/"):
            from flask import request as flask_request
            from src.services.tools import jwt_decode
            result = jwt_decode(flask_request)
        assert result is False

    def test_invalid_token_returns_false(self, app):
        with app.test_request_context("/", headers={"Cookie": "access_token=garbage"}):
            from flask import request as flask_request
            from src.services.tools import jwt_decode
            result = jwt_decode(flask_request)
        assert result is False
