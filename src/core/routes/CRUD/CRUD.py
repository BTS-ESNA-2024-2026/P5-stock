from src.core.decorators.decorators import *
from database.model import db, Room, Base_, Asset
from flask import Blueprint, request
from src.core.routes.CRUD.CRUD_tools import create, read, update, delete

CRUD = Blueprint("CRUD", __name__)

# - - - - - - - - ROOM - - - - - - - - 
@CRUD.post("/room")
@require_technician
def insert_room():
    element = "room"
    required_fields = ["base_id", "room"]
    accetpable_fields = []
    obj = Room()

    data = request.json
    return create(element, required_fields, accetpable_fields, data, obj)

@CRUD.get("/room/<int:ID>")
@require_technician
def get_room(ID):
    element = "room"
    obj = db.session.query(Room).filter(Room.id == ID).first()

    return read(ID, element, obj)

@CRUD.put("/room/<int:ID>")
@require_technician
def update_room(ID):
    element = "room"
    updatable_fields = ['base_id', 'room']
    obj = db.session.query(Room).filter(Room.id == ID).first()

    data = request.json
    return update(ID, element, updatable_fields, data, obj)

@CRUD.delete("/room/<int:ID>")
@require_technician
def delete_room(ID):
    element = "room"
    obj = db.session.query(Room).filter(Room.id == ID).first()

    return delete(ID, element, obj)



# - - - - - - - - BASE - - - - - - - - 
@CRUD.post("/base")
@require_technician
def insert_base():
    element = "base"
    required_fields = ["name", "address"]
    accetpable_fields = []
    obj = Base_()

    data = request.json
    return create(element, required_fields, accetpable_fields, data, obj)

@CRUD.get("/base/<int:ID>")
@require_technician
def get_base(ID):
    element = "base"
    obj = db.session.query(Base_).filter(Base_.id == ID).first()

    return read(ID, element, obj)

@CRUD.put("/base/<int:ID>")
@require_technician
def update_base(ID):
    element = "base"
    updatable_fields = ['name', 'address']
    obj = db.session.query(Base_).filter(Base_.id == ID).first()

    data = request.json
    return update(ID, element, updatable_fields, data, obj)

@CRUD.delete("/base/<int:ID>")
@require_technician
def delete_base(ID):
    element = "base"
    obj = db.session.query(Base_).filter(Base_.id == ID).first()

    return delete(ID, element, obj)



# BIG ISSUE ON STATUS/quantity/BOOL --> not validated



# - - - - - - - - ASSET - - - - - - - - 
@CRUD.post("/asset")
@require_technician
def insert_asset():
    element = "asset"
    required_fields = ["type_asset_id", "name", "status"]
    accetpable_fields = ["mission_id", "room_id", "number", "quantity", "shelf", "sensible"]
    obj = asset()

    data = request.json
    return create(element, required_fields, accetpable_fields, data, obj)

@CRUD.get("/asset/<int:ID>")
@require_technician
def get_asset(ID):
    element = "asset"
    obj = db.session.query(asset).filter(asset.id == ID).first()

    return read(ID, element, obj)

@CRUD.put("/asset/<int:ID>")
@require_technician
def update_asset(ID):
    element = "asset"
    updatable_fields = ["type_asset_id", "mission_id", "name", "room_id", "number", "status", "quantity", "shelf", "sensible"]
    obj = db.session.query(asset).filter(asset.id == ID).first()

    data = request.json
    return update(ID, element, updatable_fields, data, obj)

@CRUD.delete("/asset/<int:ID>")
@require_technician
def delete_asset(ID):
    element = "asset"
    obj = db.session.query(asset).filter(asset.id == ID).first()

    return delete(ID, element, obj)