from functools import wraps

from flask import jsonify, request

from src.services.tools import jwt_decode


def _unauthorized():
    return jsonify({'error': 'Invalid token'}), 401


def _forbidden():
    return jsonify({'error': 'No right to go here'}), 403


def require_viewer(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = jwt_decode(request)
        if not user:
            return _unauthorized()
        if user.role.name == 'viewer':
            return f(*args, **kwargs)
        return require_user(f)(*args, **kwargs)
    return decorated_function


def require_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = jwt_decode(request)
        if not user:
            return _unauthorized()
        if user.role.name == 'user':
            return f(*args, **kwargs)
        return require_secure_user(f)(*args, **kwargs)
    return decorated_function


def require_secure_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = jwt_decode(request)
        if not user:
            return _unauthorized()
        if user.role.name == 'secure_user':
            return f(*args, **kwargs)
        return require_technician(f)(*args, **kwargs)
    return decorated_function


def require_technician(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = jwt_decode(request)
        if not user:
            return _unauthorized()
        if user.role.name == 'technician':
            return f(*args, **kwargs)
        return require_admin(f)(*args, **kwargs)
    return decorated_function


def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = jwt_decode(request)
        if not user:
            return _unauthorized()
        if user.role.name == 'admin':
            return f(*args, **kwargs)
        return _forbidden()
    return decorated_function
