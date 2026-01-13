from typing import re

from argon2.exceptions import VerifyMismatchError

from database.model import db, User, ph


def get_user_by_username(username):
    return db.session.query(User).filter(User.username == username).first()

def validate_username(username):
    if len(username) < 3 or len(username) > 25:
        return False
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False
    forbidden_words = ['admin', 'root', 'system', 'null', 'undefined', 'select', 'drop', 'insert']
    if username.lower() in forbidden_words:
        return False
    return True

def verify_password(plain: str, hashed: str) -> bool:
    try:
        ph.verify(hashed, plain)
        return True
    except VerifyMismatchError:
        return False
