import re
from uuid import UUID

import jwt
from argon2.exceptions import VerifyMismatchError
from loguru import logger

from src.database.model import AssetType, User, db, ph
from src.services.crypto import JWT_ALGORITHM, JWT_AUDIENCE, JWT_ISSUER, get_public_key


def get_user_by_username(username):
    return db.session.query(User).filter(User.username == username).first()

def get_user_by_id(user_id):
    return db.session.query(User).filter(User.id == user_id).first()

def get_asset_type_by_type(asset_type):
    return db.session.query(AssetType).filter(AssetType.type == asset_type).first()

def validate_username(username):
    if not isinstance(username, str):
        return False
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

    try:
        payload = jwt.decode(
            token,
            get_public_key(),
            algorithms=[JWT_ALGORITHM],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
            options={'require': ['exp', 'iat', 'user_id']},
        )
        request.user_data = payload

    except jwt.ExpiredSignatureError:
        logger.info("JWT expired")
        return False
    except jwt.InvalidAudienceError:
        logger.warning("JWT invalid audience")
        return False
    except jwt.InvalidIssuerError:
        logger.warning("JWT invalid issuer")
        return False
    except jwt.InvalidSignatureError:
        logger.warning("JWT invalid signature")
        return False
    except jwt.DecodeError:
        logger.warning("JWT decode error")
        return False
    except jwt.MissingRequiredClaimError as exc:
        logger.warning(f"JWT missing required claim: {exc}")
        return False
    except Exception as exc:
        logger.error(f"JWT decode unexpected error: {exc}")
        return False
    try:
        user_id = UUID(request.user_data['user_id'])
    except (KeyError, ValueError, TypeError):
        return False
    user = get_user_by_id(user_id)
    if not user or not user.active:
        return False
    return user

