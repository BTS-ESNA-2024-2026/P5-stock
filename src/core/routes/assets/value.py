from src.core.decorators.decorators import require_user
from database.model import db, Value
from loguru import logger
from flask import Blueprint, request, make_response, jsonify
from datetime import datetime
from sqlalchemy.exc import IntegrityError

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

@values_blueprint.put("/value/<int:value_id>") # if changed value == value, ignore and send 200
@require_user
def update_value(value_id):
    try:
        value = db.session.query(Value).filter(Value.id == value_id).first()
        if not value:
            return jsonify({
                'error': 'Value not found',
                'status': 'error'
            }), 404
        data = request.json
        updatable_fields = ['asset_id', 'spec_id', 'value']
        updated = False
        for field in updatable_fields:
            if field in data:
                try:
                    setattr(value, field, data[field])
                    updated = True
                except ValueError as e:
                    logger.error(f"Invalid value for {field}: {e}")
                    return jsonify({
                        'error': f'Invalid value for {field}',
                        'status': 'error'
                    }), 400
        if not updated:
            logger.error(f"Failed to update value, no valid field for value {value_id}")
            return jsonify({
                'error': 'No valid update fields provided',
                'status': 'error'
            }), 400
        
        value.DE = datetime.utcnow()
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Failed to update value, invalid foreign key for value {value_id}: {e}")
            return jsonify({
                'error': 'Foreign key constraint failed, please verify IDs',
                'status': 'error'
            }), 400
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update value, unknown error for value {value_id}: {e}")
            return jsonify({
                'error': 'Internal server error',
                'status': 'error'
            }), 500

        logger.info(f"Value updated by {request.current_user.id} : {value_id}")
        return jsonify({
            'message': 'Value updated',
            'status': 'success'
        }), 200
    
    except TypeError as e:
        logger.error(f"Failed to update value: {e}")
        return jsonify({
            'error': "Internal server error on value update",
            'status': 'error'
        }), 500