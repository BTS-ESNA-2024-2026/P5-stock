from loguru import logger

from database.model import db, Spec, AssetType
from src.core.decorators.decorators import require_jwt, require_user
from flask import Blueprint, render_template, request, make_response, jsonify

from src.core.tools import validate_username, get_asset_type_by_type

asset_type_blueprint = Blueprint("asset_type", __name__)

@asset_type_blueprint.post("/asset_type")
@require_user
def post_specs():
    TYPE = request.json.get("type")
    # Fonction qui vérifie si name entre 2 et 25 caractère uniquement alphanumérique
    if not TYPE or not validate_username(TYPE):
        return make_response(jsonify({
            'message': 'Type needs to be alphanumeric and between 2 and 25 characters'
        }), 401)
    asset_type = get_asset_type_by_type(TYPE)
    if asset_type :
        return make_response(jsonify({
            'message': 'Type already exists'
        }), 401)
    try:
        asset_type = AssetType(type=TYPE)
        db.session.add(asset_type)
        db.session.commit()
        logger.info(f"Created new asset type: {asset_type.id} by {request.current_user.id}")
        return make_response(jsonify({
            'message': 'Created new asset type'
        }),201)
    except Exception as e:
        logger.error(e)
        return make_response(jsonify({
            'message': 'Internal server error'
        }),500)

