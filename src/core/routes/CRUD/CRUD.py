from src.core.decorators.decorators import *
from database.model import db, Room, Base_, Asset, AssetType, Spec, Value, Mission
from flask import Blueprint, request
from src.core.routes.CRUD.CRUD_tools import create, read, update, delete, err, nf_err
from datetime import datetime

CRUD = Blueprint("CRUD", __name__)

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
                        t = datetime.utcnow()
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
                        obj.DE = datetime.utcnow()
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
