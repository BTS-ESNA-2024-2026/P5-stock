import re
from uuid import UUID
import jwt
from loguru import logger
from argon2.exceptions import VerifyMismatchError

from src.database.model import db, User, ph, AssetType


def get_user_by_username(username):
    return db.session.query(User).filter(User.username == username).first()

def get_user_by_id(user_id):
    return db.session.query(User).filter(User.id == user_id).first()

def get_asset_type_by_type(asset_type):
    return db.session.query(AssetType).filter(AssetType.type == asset_type).first()

def validate_username(username):
    if len(username) < 2 or len(username) > 35:
        return False
    forbidden_words = ['admin', 'root', 'system', 'null', 'undefined', 'select', 'drop', 'insert']
    if username.lower() in forbidden_words:
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
        logger.error(f"Token expired : {token}")
        return False
    except jwt.InvalidSignatureError:
        logger.error(f"Signature valide Error : {token}")
        return False
    except jwt.DecodeError:
        logger.error(f"Token decode Error : {token}")
        return False
    except Exception as e:
        logger.error(f"Unknown error in token ({e}) : {token}")
        return False
    return get_user_by_id(UUID(request.user_data['user_id']))

