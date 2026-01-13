from flask import Blueprint, render_template

from src.core.decorators.decorators import require_jwt

base_blueprint = Blueprint("base", __name__)


@base_blueprint.route("/")
@require_jwt
def index():
    return render_template("dashboard.html")