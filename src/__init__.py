from pathlib import Path
from flask import Flask
from src.database.config import Config
from src.database.model import db
from src.database.init_db import init_db
from src.services.config import limiter
from src.services.logs import setup_logger
from src.middleware import register_middleware
from dotenv import load_dotenv

from src.routes.root import root_blueprint
from src.routes.auth import auth_blueprint
from src.routes.API.CRUD import CRUD



env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    init_db(app)
    setup_logger(app)
    limiter.init_app(app)
    register_middleware(app)

    app.register_blueprint(root_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(CRUD)
    return app