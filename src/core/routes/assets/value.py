from src.core.decorators.decorators import require_user
from database.model import db, Value
from loguru import logger
from flask import Blueprint, request, make_response, jsonify
from datetime import datetime

values_blueprint = Blueprint("values", __name__)

@values_blueprint.post("/value")
@require_user
def insert_value():
    try:
        data = request.json
        try :
            value = Value(
                asset_id=data["asset_id"],
                spec_id=data["spec_id"],
                DA = datetime.utcnow(),
                DE = datetime.utcnow(),
                value = data["value"],
            )

        except KeyError as e:
            logger.error(f"Couldn't create value, missing fields : {e}")
            return jsonify({
                'error': 'Missing required fields',
                'status': 'error'
            }), 400

        db.session.add(value)
        try :
            db.session.commit()
        except IntegrityError as e :
            logger.error(f"Couldn't create value, invalid foreing key : {e}")
            return jsonify({
                'error': 'foreign key constraint failed, please verify IDs',
                'status': 'error'
            }), 400
        except Exception as e :
            logger.error(f"Couldn't create value, unknown error : {e}")
            return jsonify({
                'error': 'Internal server error',
                'status': 'error'
            }), 500
        logger.info(f"New value by {request.current_user.id} : {value.id}")
        return jsonify({
            'message': 'Value created',
            'status': 'success'
        }), 201

    except TypeError as e:
        logger.error(f"Couldn't create value : {e}")
        return jsonify({
            'error': "Internal server error on value creation",
            'status': 'error'
        }), 500