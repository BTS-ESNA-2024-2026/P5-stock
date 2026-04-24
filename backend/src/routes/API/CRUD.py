from datetime import datetime, UTC
from functools import wraps

from flask import Blueprint, jsonify, request

from src.database.model import (
    Asset,
    AssetType,
    Base_,
    Log,
    Mission,
    Role,
    Room,
    Spec,
    User,
    Value,
    db,
)
from src.services.CRUD_tools import _serialize_value, create, delete, err, nf_err, read, update
from src.services.decorators import require_admin, require_technician, require_viewer

CRUD = Blueprint("CRUD", __name__)


def _serialize_obj(obj):
    return {
        col.name: _serialize_value(getattr(obj, col.name))
        for col in obj.__table__.columns
        if getattr(obj, col.name) is not None
    }


# ========== LIST ENDPOINTS ==========

@CRUD.get("/assets")
@require_viewer
def list_assets():
    assets = db.session.query(Asset).all()
    result = []
    for a in assets:
        item = _serialize_obj(a)
        if a.asset_type:
            item['type_name'] = a.asset_type.type
        if a.room:
            item['room_name'] = a.room.room
            if a.room.base:
                item['base_name'] = a.room.base.name
        if a.mission:
            item['mission_title'] = a.mission.title
        result.append(item)
    return jsonify(result), 200


@CRUD.get("/asset_types")
@require_viewer
def list_asset_types():
    types = db.session.query(AssetType).all()
    return jsonify([_serialize_obj(t) for t in types]), 200


@CRUD.get("/rooms")
@require_viewer
def list_rooms():
    rooms = db.session.query(Room).all()
    result = []
    for r in rooms:
        item = _serialize_obj(r)
        if r.base:
            item['base_name'] = r.base.name
        result.append(item)
    return jsonify(result), 200


@CRUD.get("/bases")
@require_viewer
def list_bases():
    bases = db.session.query(Base_).all()
    return jsonify([_serialize_obj(b) for b in bases]), 200


@CRUD.get("/missions")
@require_viewer
def list_missions():
    missions = db.session.query(Mission).all()
    result = []
    for m in missions:
        item = _serialize_obj(m)
        item['asset_count'] = len(m.assets)
        result.append(item)
    return jsonify(result), 200


@CRUD.get("/users")
@require_admin
def list_users():
    users = db.session.query(User).all()
    result = []
    for u in users:
        item = {
            'id': str(u.id),
            'username': u.username,
            'name': u.name,
            'active': u.active,
            'group_id': str(u.group_id),
            'DA': u.DA.isoformat() if u.DA else None,
            'DE': u.DE.isoformat() if u.DE else None,
        }
        if u.role:
            item['role_name'] = u.role.name
        result.append(item)
    return jsonify(result), 200


@CRUD.get("/roles")
@require_viewer
def list_roles():
    roles = db.session.query(Role).all()
    return jsonify([_serialize_obj(r) for r in roles]), 200


@CRUD.get("/logs")
@require_viewer
def list_logs():
    logs = db.session.query(Log).order_by(Log.D.desc()).limit(50).all()
    result = []
    for log_entry in logs:
        item = _serialize_obj(log_entry)
        if log_entry.asset:
            item['asset_name'] = log_entry.asset.name
        result.append(item)
    return jsonify(result), 200

class CRUDHandler:
    @staticmethod
    def crud_operation(model_class, element, operation_type,
        required_fields=None,
        acceptable_fields=None,
        updatable_fields=None):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    if operation_type not in ["create", "get", "update", "delete"]:
                        return err(400, "CRUD operation without valid operation type", *args, **kwargs)

                    if operation_type == 'create':
                        data = request.json
                        obj = model_class()
                        t = datetime.now(UTC)
                        obj.DE = t
                        obj.DA = t
                        return create(element, required_fields, acceptable_fields or [], data, obj)

                    #existing object section
                    ID = kwargs.get('ID')
                    obj = db.session.query(model_class).filter(model_class.id == ID).first()

                    if not obj:
                        return nf_err(element, args)

                    if operation_type == 'get':
                        return read(ID, element, obj)

                    elif operation_type == 'update':
                        data = request.json
                        obj.DE = datetime.now(UTC)
                        return update(ID, element, updatable_fields, data, obj)

                    elif operation_type == 'delete':
                        return delete(ID, element, obj)

                except Exception as e:
                    db.session.rollback()
                    return err(500, "Internal server error", e, *args, **kwargs)
                return err(500, "Internal server error", *args, **kwargs)

            return wrapper
        return decorator



# - - - - - - - - ROOM - - - - - - - -
@CRUD.post("/room")
@require_technician
@CRUDHandler.crud_operation(Room, "room", "create",
    required_fields=["base_id", "room"])
def insert_room():
    pass

@CRUD.get("/room/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(Room, "room", "get")
def get_room(ID):
    pass

@CRUD.put("/room/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(Room, "room", "update",
    updatable_fields=['base_id', 'room'])
def update_room(ID):
    pass

@CRUD.delete("/room/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(Room, "room", "delete")
def delete_room(ID):
    pass



# - - - - - - - - BASE - - - - - - - -
@CRUD.post("/base")
@require_technician
@CRUDHandler.crud_operation(Base_, "base", "create",
    required_fields=["name", "address"])
def insert_base():
    pass

@CRUD.get("/base/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(Base_, "base", "get")
def get_base(ID):
    pass

@CRUD.put("/base/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(Base_, "base", "update",
    updatable_fields=['name', 'address'])
def update_base(ID):
    pass

@CRUD.delete("/base/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(Base_, "base", "delete")
def delete_base(ID):
    pass



# - - - - - - - - ASSET - - - - - - - - --> TO BE DONE need ENUM verification with fetch from DB
@CRUD.post("/asset")
@require_technician
@CRUDHandler.crud_operation(Asset, "asset", "create",
    #required_fields=["type_asset_id", "name", "status"],
    required_fields=["type_asset_id","name", "status"],
    acceptable_fields=["mission_id", "room_id", "number", "quantity", "shelf", "sensible"])
def insert_asset():
    pass

@CRUD.get("/asset/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(Asset, "asset", "get")
def get_asset(ID):
    pass

@CRUD.put("/asset/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(Asset, "asset", "update",
    updatable_fields=["mission_id", "room_id", "name", "number", "status", "quantity", "shelf", "sensible"])
def update_asset(ID):
    pass

@CRUD.delete("/asset/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(Asset, "asset", "delete")
def delete_asset(ID):
    pass



# - - - - - - - - ASSET_TYPE - - - - - - - -
@CRUD.post("/asset_type")
@require_technician
@CRUDHandler.crud_operation(AssetType, "asset_type", "create",
    required_fields=["type"])
def insert_asset_type():
    pass

@CRUD.get("/asset_type/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(AssetType, "asset_type", "get")
def get_asset_type(ID):
    pass

@CRUD.put("/asset_type/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(AssetType, "asset_type", "update",
    updatable_fields=["type"])
def update_asset_type(ID):
    pass

@CRUD.delete("/asset_type/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(AssetType, "asset_type", "delete")
def delete_asset_type(ID):
    pass



# - - - - - - - - SPEC - - - - - - - -
@CRUD.post("/spec")
@require_technician
@CRUDHandler.crud_operation(Spec, "spec", "create",
    required_fields=["type_id", "name"])
def insert_spec():
    pass

@CRUD.get("/spec/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(Spec, "spec", "get")
def get_spec(ID):
    pass

@CRUD.put("/spec/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(Spec, "spec", "update",
    updatable_fields=["type_id", "name"])
def update_spec(ID):
    pass

@CRUD.delete("/spec/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(Spec, "spec", "delete")
def delete_spec(ID):
    pass


# - - - - - - - - VALUE - - - - - - - -
@CRUD.post("/value")
@require_technician
@CRUDHandler.crud_operation(Value, "value", "create",
    required_fields=["asset_id", "spec_id", "value"])
def insert_value():
    pass

@CRUD.get("/value/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(Value, "value", "get")
def get_value(ID):
    pass

@CRUD.put("/value/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(Value, "value", "update",
    updatable_fields=["asset_id", "spec_id", "value"])
def update_value(ID):
    pass

@CRUD.delete("/value/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(Value, "value", "delete")
def delete_value(ID):
    pass




# - - - - - - - - MISSION - - - - - - - -
@CRUD.post("/mission")
@require_technician
@CRUDHandler.crud_operation(Mission, "mission", "create",
    required_fields=["title", "status", "theatre"],
    acceptable_fields=["date_start", "date_end", "description"])
def insert_mission():
    pass

@CRUD.get("/mission/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(Mission, "mission", "get")
def get_mission(ID):
    pass

@CRUD.put("/mission/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(Mission, "mission", "update",
    updatable_fields=["title", "status", "theatre", "date_start", "date_end", "description"])
def update_mission(ID):
    pass

@CRUD.delete("/mission/<uuid:ID>")
@require_technician
@CRUDHandler.crud_operation(Mission, "mission", "delete")
def delete_mission(ID):
    pass
