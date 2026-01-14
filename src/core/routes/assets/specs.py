from loguru import logger
from database.model import db, Spec
from src.core.decorators.decorators import require_user
from flask import Blueprint, request, make_response, jsonify
from src.core.tools import validate_username

specs_blueprint = Blueprint("specs", __name__)

@specs_blueprint.post("/specs")
@require_user
def post_specs():
    type_id = request.json.get('type_id')
    name = request.json.get('name')
    #Fonction qui vérifie si name entre 2 et 35 caractère uniquement alphanumérique
    if not name or not validate_username(name):
        return make_response(jsonify({
            'message': 'Name needs to be alphanumeric and between 2 and 35 characters'
        }), 400)
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
        }), 400


