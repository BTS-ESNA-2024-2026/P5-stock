from flask import Blueprint, render_template, send_from_directory, send_file
from src.core.decorators.decorators import require_technician, require_viewer, require_user
from loguru import logger
from pathlib import Path
import os

root_blueprint = Blueprint("root", __name__)


@root_blueprint.route("/")
def root():
    # Serve the React app from the dist folder
    backend_dir = Path(__file__).parent.parent.parent
    dist_path = backend_dir.parent.parent / 'frontend' / 'dist' / 'index.html'
    
    if dist_path.exists():
        return send_file(str(dist_path))
    return "Frontend not found", 404

@root_blueprint.route('/<path:path>')
def serve_static(path):
    """Serve static files or fallback to index.html for SPA routing"""
    backend_dir = Path(__file__).parent.parent.parent
    dist_folder = backend_dir.parent.parent / 'frontend' / 'dist'
    file_path = dist_folder / path
    
    # Check if file exists
    if file_path.exists() and file_path.is_file():
        return send_from_directory(str(dist_folder), path)
    
    # Fallback to index.html for client-side routing
    index_path = dist_folder / 'index.html'
    if index_path.exists():
        return send_file(str(index_path))
    
    return "Not Found", 404

@root_blueprint.route('/favicon.ico') # required for *soup* reasons
def favicon():
    return send_from_directory('static', 'favicon.ico') # <-- soup

@root_blueprint.route("/dashboard")
@require_technician
def dash():
    return render_template("dashboard.html")