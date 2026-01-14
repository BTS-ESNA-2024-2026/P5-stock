from src.core.decorators.decorators import require_user
from database.model import db, Asset
from loguru import logger
from flask import Blueprint, render_template, request, make_response, jsonify
from datetime import datetime
from sqlalchemy.exc import IntegrityError

assets_blueprint = Blueprint("assets", __name__)

@assets_blueprint.post("/asset")
@require_user
def insert_asset():
    try:
        data = request.json
        try :
            if data["status"] in ['STOCK', 'DESTROYED', 'SOLD', 'LOST', 'TRANSIT', 'PURCHASED']:
                asset = Asset(
                    type_asset_id=data["asset_type_id"], # required is dict["var"], optional is dict.get("var") and return none if it doesn't exist
                    room_id=data.get("room_id"), # no mission ID on create
                    DA = datetime.utcnow(),
                    DE = datetime.utcnow(),
                    name = data["name"],
                    number=data.get("number"),
                    status = data["status"],
                    quantity=data.get("quantity"),
                    shelf=data.get("shelf"),
                    sensible=data.get("sensible")
                )
                
            else :
                logger.error(f"Couldn't create asset, invalid status : {e}")
                return jsonify({
                    'error': 'status must be "STOCK", "DESTROYED", "SOLD", "LOST", "TRANSIT" or "PURCHASED"',
                    'status': 'error'
                }), 400

        except KeyError as e:
            logger.error(f"Couldn't create asset, missing fields : {e}")
            return jsonify({
                'error': 'Missing required fields',
                'status': 'error'
            }), 400

        db.session.add(asset)
        try :
            db.session.commit()
        except IntegrityError as e :
            logger.error(f"Couldn't create asset, invalid foreing key : {e}")
            return jsonify({
                'error': 'foreign key constraint failed, please verify IDs',
                'status': 'error'
            }), 400
        except Exception as e :
            logger.error(f"Couldn't create asset : {e}")
            return jsonify({
                'error': 'Internal server error',
                'status': 'error'
            }), 500
        logger.info(f"New asset by {request.current_user.id} : {asset.id}/{asset.name}")
        return jsonify({
            'message': 'Asset created',
            'status': 'success'
        }), 201

    except TypeError as e:
        logger.error(f"Couldn't create asset : {e}")
        return jsonify({
            'error': "Internal server error on asset creation",
            'status': 'error'
        }), 500