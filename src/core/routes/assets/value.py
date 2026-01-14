from src.core.decorators.decorators import require_user
from database.model import db, Asset
from loguru import logger
from flask import Blueprint, render_template, request, make_response, jsonify
from datetime import datetime

assets_blueprint = Blueprint("assets", __name__)

@assets_blueprint.post("/value")
@require_user
def insert_asset():
    try:
        data = request.json
        try :
            asset = Asset(
                asset_id=data["asset_type_id"], # required is dict["var"], optional is dict.get("var") and return none if it doesn't exist
                spec_id=data.get("room_id"),
                DA = datetime.utcnow(),
                DE = datetime.utcnow(),
                value = data["value"],
            )

        except KeyError as e:
            logger.error(f"Couldn't create asset, missing fields : {e}")
            return jsonify({
                'error': 'Missing required fields',
                'status': 'error'
            }), 406

        db.session.add(asset)
        try :
            db.session.commit()
        except IntegrityError as e :
            logger.error(f"Couldn't create asset, invalid foreing key : {e}")
            return jsonify({
                'error': 'foreign key constraint failed, please verify IDs',
                'status': 'error'
            }), 406
        logger.info(f"New asset by {user.id} : {asset.id}/{asset.name}")
        return jsonify({
            'message': 'Asset created'
        }), 201

    except TypeError as e:
        logger.error(f"Couldn't create asset : {e}")
        return jsonify({
            'error': "Internal server error on asset creation",
            'status': 'error'
        }), 500