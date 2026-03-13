from flask import Blueprint, render_template, send_from_directory, jsonify
from src.services.decorators import require_technician, require_viewer, require_user
from loguru import logger

root_blueprint = Blueprint("root", __name__)


@root_blueprint.route("/")
def root():
    return render_template("root.html")

@root_blueprint.route('/favicon.ico') # required for *soup* reasons
def favicon():
    return send_from_directory('static', 'favicon.ico') # <-- soup

@root_blueprint.route("/health", methods=["GET"])
def health():
    """Health check endpoint for Docker/Kubernetes health probes"""
    return jsonify({"status": "healthy", "service": "p5-stock-backend"}), 200

@root_blueprint.route("/dashboard")
@require_technician
def dash():
    return render_template("dashboard.html")