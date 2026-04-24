import os

from flask import Blueprint, jsonify, redirect, send_from_directory

from src.services.decorators import require_technician

root_blueprint = Blueprint("root", __name__)


def _frontend_url(path: str = "") -> str:
    base = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
    suffix = f"/{path.lstrip('/')}" if path else ""
    return f"{base}{suffix}"


@root_blueprint.route("/")
def root():
    return redirect(_frontend_url("/login"), code=302)

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
    return redirect(_frontend_url("/dashboard"), code=302)


@root_blueprint.route("/assets")
@require_technician
def assets():
    return redirect(_frontend_url("/assets"), code=302)


@root_blueprint.route("/adminpanel")
@require_technician
def adminpanel():
    return redirect(_frontend_url("/adminpanel"), code=302)


@root_blueprint.route("/missions")
@require_technician
def missions():
    return redirect(_frontend_url("/missions"), code=302)


@root_blueprint.route("/users")
@require_technician
def users():
    return redirect(_frontend_url("/users"), code=302)


@root_blueprint.route("/reports")
@require_technician
def reports():
    return redirect(_frontend_url("/reports"), code=302)
