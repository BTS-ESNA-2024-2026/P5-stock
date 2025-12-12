import os
from functools import wraps
from flask import request, jsonify, current_app
import jwt
import random as r


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

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Invalid token'}), 401
        except jwt.InvalidSignatureError:
            return jsonify({'error': 'Invalid token'}), 401
        except jwt.DecodeError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            print(token)
            print(e)
            return jsonify({'error': 'Server error'}), 500

        return f(*args, **kwargs)

    return decorated_function