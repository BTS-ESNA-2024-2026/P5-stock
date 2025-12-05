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
                return jsonify({'error': 'Token manquant'}), 418
            return jsonify({'error': 'Token manquant'}), 401

        try:
            payload = jwt.decode(
                token,
                os.getenv('SECRET_KEY'),
                algorithms=['HS256']
            )
            request.user_data = payload

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expiré'}), 401
        except jwt.InvalidSignatureError:
            return jsonify({'error': 'Signature invalide'}), 401
        except jwt.DecodeError:
            return jsonify({'error': 'Token invalide'}), 401
        except Exception as e:
            print(token)
            print(e)
            return jsonify({'error': 'Erreur de validation du token'}), 401

        return f(*args, **kwargs)

    return decorated_function