import os
from datetime import UTC, datetime, timedelta

import jwt
import pyotp
from flask import Blueprint, jsonify, make_response, redirect, request
from loguru import logger

from src.database.model import db
from src.services.config import limiter
from src.services.crypto import JWT_ALGORITHM, JWT_AUDIENCE, JWT_ISSUER, get_private_key
from src.services.tools import (
    get_user_by_username,
    jwt_decode,
    verify_password,
)

auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")

# Cookies marked Secure are dropped by browsers over plain HTTP except on
# localhost. Allow disabling for development behind a non-HTTPS reverse proxy.
COOKIE_SECURE = os.getenv('COOKIE_SECURE', 'true').lower() != 'false'

@auth_blueprint.get("/login")
def get_login():
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
    return redirect(f"{frontend_url}/login", code=302)

@auth_blueprint.post("/login")
@limiter.limit("5 per minute")
def post_login():
    try:
        age=20 # minutes
        username = request.form.get('username')
        password = request.form.get('password')
        otp_code = request.form.get('otp_code')
        if not username or not password:
            return jsonify({'message': 'Username and password are needed'}), 401
        user = get_user_by_username(username)
        if not user or not verify_password(password, user.hash):
            return jsonify({
                'message': 'Username or password incorrect',
            }), 401

        if not user.active:
            logger.info(f"Login refused: account {user.id} is disabled")
            return jsonify({
                'message': 'Compte desactive, contactez un administrateur',
            }), 403

        if user.MFA:
            if not otp_code:
                return jsonify({'message': 'OTP code required'}), 401
            totp = pyotp.TOTP(user.MFA)
            if not totp.verify(otp_code, valid_window=1):
                return jsonify({'message': 'Invalid OTP code'}), 401

        now = datetime.now(UTC)
        access_payload = {
            'user_id': str(user.id),
            'exp': now + timedelta(minutes=age),
            'iat': now,
            'iss': JWT_ISSUER,
            'aud': JWT_AUDIENCE,
            'type': 'access',
        }
        access_token = jwt.encode(access_payload, get_private_key(), algorithm=JWT_ALGORITHM)
        response = make_response(jsonify({
                'message': 'Login successful',
            }), 200)
        response.set_cookie(
                'access_token',
                access_token,
                httponly=True,        # Prevent XSS reading the token
                secure=COOKIE_SECURE, # HTTPS only in production
                samesite='Strict',    # CSRF protection (ANSSI required)
                max_age=age * 60,
                path='/',
            )
        logger.info(f"{user.id} logged in")
        return response
    except Exception:
        logger.exception("Unhandled error during login")
        return jsonify({
            'message': 'Internal server error',
        }), 500


# Self-registration is disabled: per UC-02 user management is admin-only and
# accounts are provisioned through `POST /api/user`. Leaving this endpoint as
# 410 Gone makes the lockdown explicit if someone calls the historic URL.
@auth_blueprint.post("/register")
def post_register():
    return jsonify({
        'message': 'Self-registration is disabled. Contact an administrator.',
    }), 410


@auth_blueprint.get("/me")
def get_me():
    user = jwt_decode(request)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify({
        'id': str(user.id),
        'username': user.username,
        'name': user.name,
        'role': user.role.name if user.role else None,
        'perms': (user.role.perms if user.role and user.role.perms else {}),
        'active': user.active,
    }), 200


@auth_blueprint.post("/logout")
def post_logout():
    response = make_response(jsonify({'message': 'Logged out'}), 200)
    response.delete_cookie('access_token', path='/')
    return response


@auth_blueprint.post("/otp/setup")
def post_otp_setup():
    user = jwt_decode(request)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=user.username, issuer_name="SGLM")
    user.MFA = secret
    user.DE = datetime.now(UTC)
    db.session.commit()
    logger.info(f"OTP setup for user {user.id}")
    return jsonify({'secret': secret, 'uri': uri}), 200


@auth_blueprint.delete("/otp/setup")
def delete_otp_setup():
    user = jwt_decode(request)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    user.MFA = None
    user.DE = datetime.now(UTC)
    db.session.commit()
    logger.info(f"OTP disabled for user {user.id}")
    return jsonify({'message': 'OTP disabled'}), 200
