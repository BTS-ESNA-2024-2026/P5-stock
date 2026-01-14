import re

import jwt
from argon2.exceptions import VerifyMismatchError

from database.model import db, User, ph, AssetType


def get_user_by_username(username):
    return db.session.query(User).filter(User.username == username).first()

def get_user_by_id(user_id):
    return db.session.query(User).filter(User.id == user_id).first()

def get_asset_type_by_type(asset_type):
    return db.session.query(AssetType).filter(AssetType.type == asset_type).first()

def validate_username(username):
    if len(username) < 2 or len(username) > 25:
        return False
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False
    return True

def verify_password(plain: str, hashed: str) -> bool:
    try:
        ph.verify(hashed, plain)
        return True
    except VerifyMismatchError:
        return False

def jwt_decode(request):
    token = request.cookies.get('access_token')

    if not token:
        return False

    public_key = open('public.pem', 'rb').read()
    try:
        payload = jwt.decode(token, public_key, algorithms=['RS256'])
        request.user_data = payload

    except jwt.ExpiredSignatureError:
        print("Token expired")
        return False
    except jwt.InvalidSignatureError:
        print("Signature valide Error")
        return False
    except jwt.DecodeError:
        print("Token decode Error")
        return False
    except Exception as e:
        print(token)
        print(e)
        return False
    return get_user_by_id(request.user_data['user_id'])

