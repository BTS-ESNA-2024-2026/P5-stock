from pathlib import Path
from flask import Flask

from database.config import Config
from database.model import db
from src.core.config import limiter
from src.core.logs import setup_logger
from src.core.middleware import register_middleware
from src.core.routes.auth.auth import auth_blueprint
from src.core.routes.root import base_blueprint
from src.core.routes.assets.asset import assets_blueprint
from dotenv import load_dotenv


env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    setup_logger(app)
    limiter.init_app(app)
    register_middleware(app)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(base_blueprint)
    app.register_blueprint(assets_blueprint)
    return app