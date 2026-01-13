from flask import Blueprint, render_template, send_from_directory
from src.core.decorators.decorators import require_technician, require_viewer, require_user
from loguru import logger

base_blueprint = Blueprint("base", __name__)


@base_blueprint.route("/")
def root():
    return render_template("root.html")

@base_blueprint.route('/favicon.ico') # required for *soup* reasons
def favicon():
    return send_from_directory('static', 'favicon.ico') # <-- soup

@base_blueprint.route("/dashboard")
@require_technician
def dash():
    return render_template("dashboard.html")