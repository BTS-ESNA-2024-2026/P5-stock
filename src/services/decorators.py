import os
from functools import wraps
from flask import request, jsonify, current_app
import jwt
import random as r

from src.services.tools import jwt_decode

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
        return jsonify({'error': 'Insufficient rights to access this ressource'}), 403
    return decorated_function