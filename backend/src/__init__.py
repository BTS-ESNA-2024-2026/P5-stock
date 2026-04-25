import os as _os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from sqlalchemy import text

from src.database.config import Config
from src.database.init_db import SEED_SQL
from src.database.model import db, migrate
from src.middleware import register_middleware
from src.routes.API.CRUD import CRUD
from src.routes.auth import auth_blueprint
from src.routes.root import root_blueprint
from src.services.config import limiter
from src.services.logs import setup_logger

env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()
        db.session.execute(text(SEED_SQL))
        db.session.commit()
    setup_logger(app)
    limiter.init_app(app)
    register_middleware(app)



    app.register_blueprint(root_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(CRUD, url_prefix="/api")
    return app

# Create app instance for Gunicorn (skipped when running under pytest)
if not _os.environ.get("PYTEST_CURRENT_TEST") and _os.environ.get("DATABASE_URL"):
    app = create_app()
