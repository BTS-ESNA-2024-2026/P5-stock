from datetime import datetime, timedelta
import os
from uuid import UUID

import jwt
import pyotp
from flask import Blueprint, redirect, request, make_response, jsonify
from loguru import logger

from src.database.model import db, User, ph
from src.services.config import limiter
from src.services.decorators import require_admin
from src.services.tools import get_user_by_username, jwt_decode, validate_username, verify_password

auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")

VIEWER_ROLE_ID = UUID('019563a0-0000-7000-8000-000000000005')

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

        if user.MFA:
            if not otp_code:
                return jsonify({'message': 'OTP code required'}), 401
            totp = pyotp.TOTP(user.MFA)
            if not totp.verify(otp_code, valid_window=1):
                return jsonify({'message': 'Invalid OTP code'}), 401

        access_payload = {
                'user_id': str(user.id),
                'exp': datetime.utcnow() + timedelta(minutes=age),
                'iat': datetime.utcnow(),
                'type': 'access'
            }
        private_key = open('private.pem', 'rb').read()
        access_token = jwt.encode(access_payload, private_key, algorithm='RS256')
        response = make_response(jsonify({
                'message': 'Login successful',
            }), 200)
        response.set_cookie(
                'access_token',
                access_token,
                httponly=True,  # Prevent XSS
                secure=True,  # HTTPS only (ANSSI required)
                samesite='Strict',  # CSRF protection (ANSSI required)
                max_age=age * 60,  # 10 minutes
                path='/'  # Explicit path
            )
        logger.info(f"{user.id} logged in")
        return response
    except Exception as e:
        logger.error(f"{e}")
        return jsonify({
            'message': 'Internal server error',
        }), 500

@auth_blueprint.post("/register")
def post_register():
    username = request.json.get('username')
    name = request.json.get('name')
    password = request.json.get('password')

    user = get_user_by_username(username)
    if not username or not password:
        return make_response(jsonify({
            'message': 'Username and password are needed'
        }), 401)
    if user :
        return make_response(jsonify({
            'message': 'User already exists'
        }), 401)
    if not validate_username(username):
        return make_response(jsonify({
            'message': 'Username needs to be alphanumeric'
        }),401)
    try:
        user = User(
            group_id=VIEWER_ROLE_ID,
            username=username,
            name = name if name else None,
            hash=ph.hash(password),
            hash_algorithm = "argon2",
        )
        db.session.add(user)
        db.session.commit()
        logger.info(f"New user created : {user.id}")
        return jsonify({
            'message': 'Account created successfully'
        }), 201

    except Exception as e:
        logger.error(e)
        return jsonify({
            'message': 'Internal Server Error',
        }), 500


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
    user.DE = datetime.utcnow()
    db.session.commit()
    logger.info(f"OTP setup for user {user.id}")
    return jsonify({'secret': secret, 'uri': uri}), 200


@auth_blueprint.delete("/otp/setup")
def delete_otp_setup():
    user = jwt_decode(request)
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    user.MFA = None
    user.DE = datetime.utcnow()
    db.session.commit()
    logger.info(f"OTP disabled for user {user.id}")
    return jsonify({'message': 'OTP disabled'}), 200
