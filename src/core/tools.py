from database.model import db, User


def get_user_by_username(username):
    return db.session.query(User).filter(User.username == username).first()

