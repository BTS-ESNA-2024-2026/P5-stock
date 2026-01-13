import os
from functools import wraps
from flask import request, jsonify, current_app
import jwt
import random as r

from src.core.tools import jwt_decode


def require_jwt(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('access_token')

        if not token:
            a = r.randint(0, 100)
            if a == 5:
                return jsonify({'error': 'Invalid token'}), 418
            return jsonify({'error': 'Invalid token'}), 401

        public_key = open('public.pem', 'rb').read()
        try:
            payload = jwt.decode(token, public_key, algorithms=['RS256'])
            request.user_data = payload
            print(request.user_data)

        except jwt.ExpiredSignatureError:
            print("Token expired")
            return jsonify({'error': 'Invalid token'}), 401
        except jwt.InvalidSignatureError:
            print("Signature valide Error")
            return jsonify({'error': 'Invalid token'}), 401
        except jwt.DecodeError:
            print("Token decode Error")
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            print(token)
            print(e)
            return jsonify({'error': 'Server error'}), 500

        return f(*args, **kwargs)

    return decorated_function


def require_viewer(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = jwt_decode(request)
        if not user:
            return jsonify({'error': 'Invalid token'}), 401

        if user.role.name == 'viewer':
            return f(*args, **kwargs)
        return require_user(f)(*args, **kwargs)
    return decorated_function

def require_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = jwt_decode(request)
        if not user:
            return jsonify({'error': 'Invalid token'}), 401
        if user.role.name == 'user':
            return f(*args, **kwargs)
        return require_secure_user(f)(*args, **kwargs)
    return decorated_function

def require_secure_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = jwt_decode(request)
        if not user:
            return jsonify({'error': 'Invalid token'}), 401
        if user.role.name == 'secure_user':
            return f(*args, **kwargs)
        return require_technician(f)(*args, **kwargs)
    return decorated_function

def require_technician(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = jwt_decode(request)
        if not user:
            return jsonify({'error': 'Invalid token'}), 401
        if user.role.name == 'technician':
            return f(*args, **kwargs)
        return require_admin(f)(*args, **kwargs)
    return decorated_function

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = jwt_decode(request)
        if not user:
            return jsonify({'error': 'Invalid token'}), 401
        if user.role.name == 'admin':
            return f(*args, **kwargs)
        return jsonify({'error': 'No right to go here'}), 403
    return decorated_function