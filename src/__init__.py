from pathlib import Path
import os

from flask import Flask, send_from_directory

from src.core.routes.auth.login import auth_blueprint
from src.core.routes.jsp import base_blueprint
from dotenv import load_dotenv


env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def create_app():
    # Get the absolute path to the project root
    project_root = Path(__file__).parent.parent.parent
    dist_folder = project_root / 'src' / 'frontend' / 'dist'
    
    app = Flask(
        __name__,
        static_folder=str(dist_folder),
        static_url_path='/',
        template_folder=str(dist_folder)
    )
    
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(base_blueprint)
    
    # Serve Vite frontend
    @app.route('/')
    def serve_root():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        file_path = os.path.join(app.static_folder, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return send_from_directory(app.static_folder, path)
        # Return index.html for SPA routing
        return send_from_directory(app.static_folder, 'index.html')
    
    return app