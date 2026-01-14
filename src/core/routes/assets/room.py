from src.core.decorators.decorators import require_technician
from database.model import db, Room
from loguru import logger
from flask import Blueprint, request, make_response, jsonify
from datetime import datetime
from sqlalchemy.exc import IntegrityError

room_blueprint = Blueprint("room", __name__)

@room_blueprint.post("/room")
@require_technician
def insert_base():
    try:
        data = request.json
        try :
            room = Room(
                base_id=data["base_id"],
                room=data["room"]
            )

        except KeyError as e:
            logger.error(f"Couldn't create room, missing fields : {e}")
            return jsonify({
                'error': 'Missing required fields',
                'status': 'error'
            }), 400

        db.session.add(room)
        try :
            db.session.commit()
        except IntegrityError as e :
            logger.error(f"Couldn't create room, invalid foreing key : {e}")
            return jsonify({
                'error': 'foreign key constraint failed, please verify IDs',
                'status': 'error'
            }), 400
        except Exception as e :
            logger.error(f"Couldn't create room, unknown error : {e}")
            return jsonify({
                'error': 'Internal server error',
                'status': 'error'
            }), 500
        logger.info(f"New room by {request.current_user.id} : {room.id}")
        return jsonify({
            'message': 'Room created',
            'status': 'success'
        }), 201

    except TypeError as e:
        logger.error(f"Couldn't create room : {e}")
        return jsonify({
            'error': "Internal server error on room creation",
            'status': 'error'
        }), 500

@room_blueprint.put("/room/<int:base_id>")
@require_technician
def update_base(base_id):
    try:
        room = db.session.query(Room).filter(Room.id == base_id).first()
        if not room:
            return jsonify({
                'error': 'Room not found',
                'status': 'error'
            }), 404
        data = request.json
        updatable_fields = ['base_id', 'room']
        updated = False
        for field in updatable_fields:
            if field in data:
                try:
                    setattr(room, field, data[field])
                    updated = True
                except BaseError as e:
                    logger.error(f"Invalid {field} for room: {e}")
                    return jsonify({
                        'error': f'Invalid {field} for room',
                        'status': 'error'
                    }), 400
        if not updated:
            logger.error(f"Failed to update room, no valid field for room {base_id}")
            return jsonify({
                'error': 'No valid update fields provided',
                'status': 'error'
            }), 400
        
        room.DE = datetime.utcnow()
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Failed to update room, invalid foreign key for room {base_id}: {e}")
            return jsonify({
                'error': 'Foreign key constraint failed, please verify IDs',
                'status': 'error'
            }), 400
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update room, unknown error for room {base_id}: {e}")
            return jsonify({
                'error': 'Internal server error',
                'status': 'error'
            }), 500

        logger.info(f"Room updated by {request.current_user.id} : {base_id}")
        return jsonify({
            'message': 'Room updated',
            'status': 'success'
        }), 200
    
    except TypeError as e:
        logger.error(f"Failed to update room: {e}")
        return jsonify({
            'error': "Internal server error on room update",
            'status': 'error'
        }), 500