from pathlib import Path

from flask import Flask

from src.core.routes.auth.login import auth_blueprint
from src.core.routes.root import base_blueprint
from dotenv import load_dotenv


env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def create_app():
    app = Flask(__name__)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(base_blueprint)
    return app