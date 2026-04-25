import os

from sqlalchemy.pool import StaticPool


class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    _db_url = os.getenv('DATABASE_URL', '')
    if ':memory:' in _db_url:
        # SQLite in-memory: use a single shared connection so that data
        # created in test fixtures is visible to subsequent requests.
        SQLALCHEMY_ENGINE_OPTIONS = {
            'connect_args': {'check_same_thread': False},
            'poolclass': StaticPool,
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }
