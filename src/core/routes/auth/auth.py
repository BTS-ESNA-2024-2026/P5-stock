import uuid
from datetime import datetime, timedelta

import jwt
from argon2 import PasswordHasher
from flask import Blueprint, render_template, request, make_response, jsonify

from database.model import db, User
from src.core.tools import get_user_by_username

auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")

ph = PasswordHasher()

@auth_blueprint.get("/login")
def get_login():
    return render_template("login.html")

@auth_blueprint.post("/login")
def post_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = get_user_by_username(username)
    print(password)
    if not user or not ph.verify(password, user.Password):
        return make_response(jsonify({
            'message': 'Email or password incorrect'
        }), 401)

    access_payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(minutes=10),
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
            max_age=10 * 60,  # 10 minutes
            path='/'  # Explicit path
        )
    return response

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
    try:
        user = User(
            group_id=5,
            username=username,
            name = name if name else None,
            hash=ph.hash(password),
            hash_algorithm = "argon2",
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'message': 'Account created successfully'
        }), 201
    except Exception as e:
        print(e)
        return jsonify({
            'message': 'Internal Server Error',
        }), 500
