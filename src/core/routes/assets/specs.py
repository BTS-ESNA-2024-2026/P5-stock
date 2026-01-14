#import os
#from datetime import datetime, timedelta
from loguru import logger

from database.model import db, Spec
from src.core.decorators.decorators import require_jwt, require_user
from flask import Blueprint, render_template, request, make_response, jsonify

from src.core.tools import validate_username

specs_blueprint = Blueprint("specs", __name__)

@specs_blueprint.get("/tmp-assets")
def get_login():
    return render_template("tmp-assets.html")

@specs_blueprint.post("/specs")
@require_user
def post_specs():
    type_id = request.json.get('type_id')
    name = request.json.get('name')
    print(request.current_user.id)
    #Fonction qui vérifie si name entre 2 et 25 caractère uniquement alphanumérique
    if not name or not validate_username(name):
        return make_response(jsonify({
            'message': 'Username needs to be alphanumeric and between 2 and 25 characters'
        }), 401)
    try:
        specs = Spec(type_id=type_id, name=name)
        db.session.add(specs)
        db.session.commit()
        logger.info(f"Created new spec: {specs.id} by {request.current_user.id}")
        return jsonify({
            'message': 'New spec created',
        }), 201
    except Exception as e:
        logger.error(f"Failed to create new spec: {e}")
        return jsonify({
            'message': 'Failed to create new spec',
        }), 401


