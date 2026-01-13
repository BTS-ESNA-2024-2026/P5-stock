from flask import Blueprint, render_template

from src.core.decorators.decorators import require_jwt

base_blueprint = Blueprint("base", __name__)


@base_blueprint.route("/")
def root():
    return render_template("root.html")

@base_blueprint.route("/dashboard")
@require_jwt
def dash():
    return render_template("dashboard.html")