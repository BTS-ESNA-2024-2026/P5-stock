from src.core.decorators.decorators import require_technician
from database.model import db, Base_
from loguru import logger
from flask import Blueprint, request, make_response, jsonify
from datetime import datetime
from sqlalchemy.exc import IntegrityError

base_blueprint = Blueprint("base", __name__)

@base_blueprint.post("/base")
@require_technician
def insert_base():
    try:
        data = request.json
        try :
            base = Base_(
                name=data["name"],
                address=data["address"]
            )

        except KeyError as e:
            logger.error(f"Couldn't create base, missing fields : {e}")
            return jsonify({
                'error': 'Missing required fields',
                'status': 'error'
            }), 400

        db.session.add(base)
        try :
            db.session.commit()
        except IntegrityError as e :
            logger.error(f"Couldn't create base, invalid foreing key : {e}")
            return jsonify({
                'error': 'foreign key constraint failed, please verify IDs',
                'status': 'error'
            }), 400
        except Exception as e :
            logger.error(f"Couldn't create base, unknown error : {e}")
            return jsonify({
                'error': 'Internal server error',
                'status': 'error'
            }), 500
        logger.info(f"New base by {request.current_user.id} : {base.id}")
        return jsonify({
            'message': 'Base created',
            'status': 'success'
        }), 201

    except TypeError as e:
        logger.error(f"Couldn't create base : {e}")
        return jsonify({
            'error': "Internal server error on base creation",
            'status': 'error'
        }), 500

@base_blueprint.put("/base/<int:base_id>")
@require_technician
def update_base(base_id):
    try:
        base = db.session.query(Base_).filter(Base_.id == base_id).first()
        if not base:
            return jsonify({
                'error': 'Base not found',
                'status': 'error'
            }), 404
        data = request.json
        updatable_fields = ['name', 'address']
        updated = False
        for field in updatable_fields:
            if field in data:
                try:
                    setattr(base, field, data[field])
                    updated = True
                except BaseError as e:
                    logger.error(f"Invalid {field} for base: {e}")
                    return jsonify({
                        'error': f'Invalid {field} for base',
                        'status': 'error'
                    }), 400
        if not updated:
            logger.error(f"Failed to update base, no valid field for base {base_id}")
            return jsonify({
                'error': 'No valid update fields provided',
                'status': 'error'
            }), 400
        
        base.DE = datetime.utcnow()
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Failed to update base, invalid foreign key for base {base_id}: {e}")
            return jsonify({
                'error': 'Foreign key constraint failed, please verify IDs',
                'status': 'error'
            }), 400
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update base, unknown error for base {base_id}: {e}")
            return jsonify({
                'error': 'Internal server error',
                'status': 'error'
            }), 500

        logger.info(f"Base updated by {request.current_user.id} : {base_id}")
        return jsonify({
            'message': 'Base updated',
            'status': 'success'
        }), 200
    
    except TypeError as e:
        logger.error(f"Failed to update base: {e}")
        return jsonify({
            'error': "Internal server error on base update",
            'status': 'error'
        }), 500