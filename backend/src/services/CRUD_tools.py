from datetime import datetime, UTC
from uuid import UUID

from flask import jsonify
from loguru import logger
from sqlalchemy.exc import ProgrammingError

#from traceback import print_exc as trcb
from src.database.model import db


def _serialize_value(val):
    """Convert non-JSON-serializable types for API responses."""
    if isinstance(val, UUID):
        return str(val)
    if isinstance(val, datetime):
        return val.isoformat()
    return val

#mode : ["read", "create", "update", "delete"]

def create(element, required_fields, acceptable_fields, data, obj=None) :
    mode = "create"
    try:
        missing = [field for field in required_fields if field not in data]
        if missing:
            return mfield_err(element, mode, data, missing=missing)
        allowed = set(required_fields + acceptable_fields)
        try:
            for field in allowed :
                if field in data :
                    setattr(obj, field, data[field])
        except Exception:
            return ifield_err(element, mode, data)
        return commit(element, obj, mode)
    except Exception as e:
        return ukn_err(element, mode, e)

def read(ID, element, obj=None) :
    mode = "read"
    if not obj :
        return nf_err(element, mode, ID)
    try:
        return {column.name: _serialize_value(getattr(obj, column.name)) for column in obj.__table__.columns if getattr(obj, column.name) is not None}
    except Exception as e:
        return ukn_err(element, mode, e)

def update(ID, element, updatable_fields, data, obj=None) :
    mode = "update"
    if not obj :
        return nf_err(element, mode, ID)
    updated = False
    try:
        for field in updatable_fields: # filter out extra fields / injections by default
            if field in data:
                try :
                    setattr(obj, field, data[field])
                    updated = True
                except Exception:
                    return ifield_err(element, mode, data)
        if not updated:
            return mfield_err(element, mode, data)
        obj.DE = datetime.now(UTC) # even if element doesn not have DE, DB will just ignore it so leave active
        return commit(element, obj, mode)
    except Exception as e:
        return ukn_err(element, mode, e)

def delete(ID, element, obj=None) :
    mode = "delete"
    if not obj :
        return nf_err(element, mode, ID)
    try:
        return commit(element, obj, mode)
    except Exception as e:
        return ukn_err(element, mode, e)

def err(code, message, *args, **kwargs): # generic error
    logger.error(f"Generic : {message} : {str(args)} | {str(kwargs)}")
    return jsonify({
        'message': message,
        'status': 'error'
    }), code

def ukn_err(elem, mode="create", *args): # unknown error
    logger.error(f"Failed to {mode} {elem}, unknown error : {str(*args)}")
    # print(trcb())
    return jsonify({
        'message': 'Internal server error',
        'status': 'error'
    }), 500

def fkc_err(elem, mode="create", *args): # foreign key constraint failed
    logger.error(f"Failed to {mode} {elem}, foreing key constraint failed / invalid query : {str(*args)}")
    return jsonify({
        'message': 'Invalid foreign key / link to other object',
        'status': 'error'
    }), 400

def mfield_err(elem, mode="create", *args, missing=None): # missing field
    logger.error(f"Failed to {mode} {elem}, missing required field.s : {str(*args)}")
    if missing :
        return jsonify({
            'message': f'Missing required field.s{f" : {missing}" if missing else ""}',
            'status': 'error'
        }), 400

def ifield_err(elem, mode="create", *args): # invalid field
    logger.error(f"Failed to {mode} {elem}, invalid field.s provided : {str(*args)}")
    return jsonify({
        'message': 'Invalid field.s provided',
        'status': 'error'
    }), 400

def nf_err(elem, mode="create", *args): #not found, mode for consistency sake
    logger.error(f"Failed to find {elem}, {str(*args)}")
    return jsonify({
        'message': 'Unable to find requested element, please check item ID',
        'status': 'error'
    }), 404

def success(elem, mode="create", *args):
    past = {"read" : "red", "create" : "created", "update" : "updated", "delete" : "deleted"}
    logger.info(f"New {elem} {past[mode]} : {str(*args)}")
    return jsonify({
        'message': f'{elem} {past[mode]} succesfully',
        'status': 'success'
    }), 201 if mode=="create" else 200

def commit(elem, obj, mode="create") :
    if mode=="create" :
        db.session.add(obj)
    elif mode=="delete" :
        db.session.delete(obj)
    try :
        db.session.commit()
    except ProgrammingError as e:
        db.session.rollback()
        return fkc_err(elem, mode, e)
    except Exception as e :
        db.session.rollback()
        return ukn_err(elem, mode, e)
    return success(elem, mode)
