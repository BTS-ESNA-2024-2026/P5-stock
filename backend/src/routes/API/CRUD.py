from datetime import UTC, datetime
from functools import wraps
from uuid import UUID

from flask import Blueprint, jsonify, request

from src.database.model import (
    Asset,
    AssetType,
    Base_,
    Log,
    LogAdmin,
    LogMission,
    Mission,
    Role,
    Room,
    Spec,
    User,
    Value,
    db,
    ph,
)
from src.services.CRUD_tools import _serialize_value, create, delete, err, nf_err, read, update
from src.services.decorators import require_admin, require_technician, require_user, require_viewer
from src.services.tools import (
    get_user_by_username,
    jwt_decode,
    validate_username,
)


def _has_sensible_access(user) -> bool:
    """True if the user's role grants the `sensible_access` permission."""
    if user is None or user is False or not getattr(user, 'role', None):
        return False
    perms = user.role.perms or {}
    return bool(perms.get('sensible_access'))


def _coerce_sensible(val):
    """Normalise the incoming `sensible` flag to a Python bool (or None)."""
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ('1', 'true', 'yes', 'on')
    return bool(val)

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
    user = jwt_decode(request)
    q = db.session.query(Asset)
    if not _has_sensible_access(user):
        q = q.filter((Asset.sensible.is_(None)) | (Asset.sensible.is_(False)))
    assets = q.all()
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
            'MFA': bool(u.MFA),
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


@CRUD.get("/specs")
@require_viewer
def list_specs():
    specs = db.session.query(Spec).all()
    result = []
    for s in specs:
        item = _serialize_obj(s)
        if s.asset_type:
            item['type_name'] = s.asset_type.type
        result.append(item)
    return jsonify(result), 200


@CRUD.get("/asset/<uuid:ID>/values")
@require_viewer
def list_asset_values(ID):
    asset = db.session.query(Asset).filter(Asset.id == ID).first()
    if not asset:
        return nf_err("asset", [])
    result = []
    for v in asset.values:
        item = _serialize_obj(v)
        if v.spec:
            item['spec_name'] = v.spec.name
        result.append(item)
    return jsonify(result), 200


@CRUD.get("/values")
@require_viewer
def list_all_values():
    """Bulk listing of values across all assets, used by AssetsPage to render
    expandable rows and to filter assets by spec/value without an N+1 fetch.
    Sensible-asset values are filtered out for users without sensible_access."""
    user = jwt_decode(request)
    has_sensible = _has_sensible_access(user)
    q = db.session.query(Value).join(Asset, Value.asset_id == Asset.id)
    if not has_sensible:
        q = q.filter((Asset.sensible.is_(None)) | (Asset.sensible.is_(False)))
    values = q.all()
    result = []
    for v in values:
        item = _serialize_obj(v)
        if v.spec:
            item['spec_name'] = v.spec.name
        result.append(item)
    return jsonify(result), 200


def _serialize_log_entry(entry, kind: str) -> dict:
    """Uniform shape for the aggregated log feed."""
    base = {
        'id': str(entry.id),
        'D': entry.D.isoformat() if entry.D else None,
        'action': entry.action,
        'log_type': kind,
    }
    if kind == 'asset':
        base.update({
            'description': entry.description,
            'asset_id': str(entry.asset_id) if entry.asset_id else None,
            'asset_name': entry.asset.name if entry.asset else None,
            'spec_id': str(entry.spec_id) if entry.spec_id else None,
            'value_id': str(entry.value_id) if entry.value_id else None,
        })
    elif kind == 'mission':
        base.update({
            'description': entry.description,
            'mission_id': str(entry.mission_id) if entry.mission_id else None,
            'entity_name': entry.mission.title if entry.mission else None,
        })
    elif kind == 'admin':
        base.update({
            'description': entry.desc,
            'user_id': str(entry.user_id) if entry.user_id else None,
            'entity_name': entry.user.username if entry.user else None,
        })
    return base


@CRUD.get("/logs")
@require_viewer
def list_logs():
    """Aggregate the three audit tables (asset/value/spec, mission, user) into a
    single recent-activity feed. The dashboard shows the top 50 most recent entries."""
    user = jwt_decode(request)
    has_sensible = _has_sensible_access(user)

    asset_logs = db.session.query(Log).order_by(Log.D.desc()).limit(50).all()
    mission_logs = db.session.query(LogMission).order_by(LogMission.D.desc()).limit(50).all()
    admin_logs = (
        db.session.query(LogAdmin).order_by(LogAdmin.D.desc()).limit(50).all()
        if user and user.role and (user.role.perms or {}).get('admin_panel')
        else []
    )

    items: list[dict] = []
    for entry in asset_logs:
        # Hide asset logs that reference a sensible asset for users without access.
        if not has_sensible and entry.asset and entry.asset.sensible:
            continue
        items.append(_serialize_log_entry(entry, 'asset'))
    for entry in mission_logs:
        items.append(_serialize_log_entry(entry, 'mission'))
    for entry in admin_logs:
        items.append(_serialize_log_entry(entry, 'admin'))

    items.sort(key=lambda x: x['D'] or '', reverse=True)
    return jsonify(items[:50]), 200


@CRUD.get("/admin/logs")
@require_technician
def list_admin_logs():
    """Read-only access to the full audit feed for admins/technicians. Logs are
    immutable (event listeners forbid update/delete on the log tables).
    Query params: ?type=asset|mission|admin (optional), ?limit=200 (max 1000)."""
    user = jwt_decode(request)
    has_sensible = _has_sensible_access(user)
    can_admin = bool(user and user.role and (user.role.perms or {}).get('admin_panel'))

    try:
        limit = max(1, min(int(request.args.get('limit', 200)), 1000))
    except ValueError:
        limit = 200
    type_filter = request.args.get('type', '')

    items: list[dict] = []

    if type_filter in ('', 'asset'):
        for entry in db.session.query(Log).order_by(Log.D.desc()).limit(limit).all():
            if not has_sensible and entry.asset and entry.asset.sensible:
                continue
            items.append(_serialize_log_entry(entry, 'asset'))

    if type_filter in ('', 'mission'):
        for entry in db.session.query(LogMission).order_by(LogMission.D.desc()).limit(limit).all():
            items.append(_serialize_log_entry(entry, 'mission'))

    if type_filter in ('', 'admin') and can_admin:
        for entry in db.session.query(LogAdmin).order_by(LogAdmin.D.desc()).limit(limit).all():
            items.append(_serialize_log_entry(entry, 'admin'))

    items.sort(key=lambda x: x['D'] or '', reverse=True)
    return jsonify(items[:limit]), 200

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



# - - - - - - - - ASSET - - - - - - - -
# Per spec (UC-3 / UC-3s): `user` may CRUD non-sensible assets; `secure_user`+ may
# touch sensible assets and toggle the `sensible` flag.
ASSET_REQUIRED = ['type_asset_id', 'name', 'status']
ASSET_ACCEPTABLE = ['mission_id', 'room_id', 'number', 'quantity', 'shelf', 'sensible']
ASSET_UPDATABLE = ['mission_id', 'room_id', 'name', 'number', 'status', 'quantity', 'shelf', 'sensible']


@CRUD.get("/asset/<uuid:ID>")
@require_user
def get_asset(ID):
    asset = db.session.query(Asset).filter(Asset.id == ID).first()
    if not asset:
        return nf_err("asset", [])
    if asset.sensible and not _has_sensible_access(jwt_decode(request)):
        return err(403, 'Insufficient permission to view a sensible asset')
    return read(ID, "asset", asset)


@CRUD.post("/asset")
@require_user
def insert_asset():
    data = request.json or {}
    user = jwt_decode(request)
    sensible = _coerce_sensible(data.get('sensible'))
    if sensible and not _has_sensible_access(user):
        return err(403, 'Insufficient permission to create a sensible asset')
    if sensible is not None:
        data = {**data, 'sensible': sensible}
    obj = Asset()
    t = datetime.now(UTC)
    obj.DA = t
    obj.DE = t
    return create("asset", ASSET_REQUIRED, ASSET_ACCEPTABLE, data, obj)


@CRUD.put("/asset/<uuid:ID>")
@require_user
def update_asset(ID):
    asset = db.session.query(Asset).filter(Asset.id == ID).first()
    if not asset:
        return nf_err("asset", [])
    user = jwt_decode(request)
    has_sensible = _has_sensible_access(user)
    if asset.sensible and not has_sensible:
        return err(403, 'Insufficient permission to edit a sensible asset')
    data = request.json or {}
    if 'sensible' in data:
        new_sensible = _coerce_sensible(data['sensible'])
        if not has_sensible and new_sensible != bool(asset.sensible):
            return err(403, 'Insufficient permission to change the sensible flag')
        data = {**data, 'sensible': new_sensible}
    asset.DE = datetime.now(UTC)
    return update(ID, "asset", ASSET_UPDATABLE, data, asset)


@CRUD.delete("/asset/<uuid:ID>")
@require_user
def delete_asset(ID):
    asset = db.session.query(Asset).filter(Asset.id == ID).first()
    if not asset:
        return nf_err("asset", [])
    if asset.sensible and not _has_sensible_access(jwt_decode(request)):
        return err(403, 'Insufficient permission to delete a sensible asset')
    return delete(ID, "asset", asset)



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
# Spec values are part of an asset's editable data, so they follow the same
# permission rules as the asset itself: any `user` may CRUD a value on a non-
# sensible asset; sensible assets require `secure_user`+.
def _value_check_asset_permission(asset_id):
    """Return None if the caller may mutate values on this asset, otherwise an
    error response tuple."""
    asset = db.session.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        return nf_err("asset", [])
    if asset.sensible and not _has_sensible_access(jwt_decode(request)):
        return err(403, 'Insufficient permission to edit values on a sensible asset')
    return None


@CRUD.post("/value")
@require_user
def insert_value():
    data = request.json or {}
    if 'asset_id' not in data:
        return err(400, 'Missing required fields: [asset_id]')
    try:
        asset_id = UUID(data['asset_id']) if isinstance(data['asset_id'], str) else data['asset_id']
    except (ValueError, TypeError):
        return err(400, 'Invalid asset_id')
    deny = _value_check_asset_permission(asset_id)
    if deny:
        return deny
    obj = Value()
    t = datetime.now(UTC)
    obj.DA = t
    obj.DE = t
    return create("value", ["asset_id", "spec_id", "value"], [], data, obj)


@CRUD.get("/value/<uuid:ID>")
@require_user
def get_value(ID):
    v = db.session.query(Value).filter(Value.id == ID).first()
    if not v:
        return nf_err("value", [])
    deny = _value_check_asset_permission(v.asset_id)
    if deny:
        return deny
    return read(ID, "value", v)


@CRUD.put("/value/<uuid:ID>")
@require_user
def update_value(ID):
    v = db.session.query(Value).filter(Value.id == ID).first()
    if not v:
        return nf_err("value", [])
    deny = _value_check_asset_permission(v.asset_id)
    if deny:
        return deny
    v.DE = datetime.now(UTC)
    return update(ID, "value", ["asset_id", "spec_id", "value"], request.json or {}, v)


@CRUD.delete("/value/<uuid:ID>")
@require_user
def delete_value(ID):
    v = db.session.query(Value).filter(Value.id == ID).first()
    if not v:
        return nf_err("value", [])
    deny = _value_check_asset_permission(v.asset_id)
    if deny:
        return deny
    return delete(ID, "value", v)




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



# - - - - - - - - USER - - - - - - - -
# Users need special handling: password hashing + uniqueness check.
# The default admin (id 019563a0-0000-7000-8000-000000000010 - 'system') and the
# bootstrap admin must remain protected from deletion.
SYSTEM_USER_IDS = {
    '019563a0-0000-7000-8000-000000000010',  # system user
}


def _serialize_user(u: User) -> dict:
    item = {
        'id': str(u.id),
        'username': u.username,
        'name': u.name,
        'active': u.active,
        'group_id': str(u.group_id),
        'DA': u.DA.isoformat() if u.DA else None,
        'DE': u.DE.isoformat() if u.DE else None,
        'has_mfa': bool(u.MFA),
    }
    if u.role:
        item['role_name'] = u.role.name
    return item


@CRUD.get("/user/<uuid:ID>")
@require_admin
def get_user(ID):
    u = db.session.query(User).filter(User.id == ID).first()
    if not u:
        return nf_err("user", [])
    return jsonify(_serialize_user(u)), 200


@CRUD.post("/user")
@require_admin
def create_user():
    data = request.json or {}
    required = ['username', 'password', 'group_id']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return err(400, f'Missing required fields: {missing}')

    username = data['username'].strip()
    if not validate_username(username):
        return err(400, 'Invalid username (alphanumeric, 2-35 chars, not reserved)')

    if get_user_by_username(username):
        return err(409, 'Username already exists')

    try:
        group_id = UUID(data['group_id']) if isinstance(data['group_id'], str) else data['group_id']
    except (ValueError, TypeError):
        return err(400, 'Invalid group_id')

    if not db.session.query(Role).filter(Role.id == group_id).first():
        return err(400, 'Role not found')

    try:
        user = User(
            username=username,
            group_id=group_id,
            name=data.get('name') or None,
            hash=ph.hash(data['password']),
            hash_algorithm='argon2',
            active=bool(data.get('active', True)),
        )
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return err(500, 'Failed to create user', e)
    return jsonify({'message': 'User created', 'id': str(user.id)}), 201


@CRUD.put("/user/<uuid:ID>")
@require_admin
def update_user(ID):
    u = db.session.query(User).filter(User.id == ID).first()
    if not u:
        return nf_err("user", [])

    data = request.json or {}
    changed = False

    if 'username' in data and data['username']:
        new_username = data['username'].strip()
        if new_username != u.username:
            if not validate_username(new_username):
                return err(400, 'Invalid username')
            if get_user_by_username(new_username):
                return err(409, 'Username already exists')
            u.username = new_username
            changed = True

    if 'name' in data:
        u.name = data['name'] or None
        changed = True

    if 'group_id' in data and data['group_id']:
        try:
            gid = UUID(data['group_id']) if isinstance(data['group_id'], str) else data['group_id']
        except (ValueError, TypeError):
            return err(400, 'Invalid group_id')
        if not db.session.query(Role).filter(Role.id == gid).first():
            return err(400, 'Role not found')
        u.group_id = gid
        changed = True

    if 'active' in data:
        u.active = bool(data['active'])
        changed = True

    if data.get('password'):
        u.hash = ph.hash(data['password'])
        u.hash_algorithm = 'argon2'
        changed = True

    if not changed:
        return err(400, 'No fields to update')

    try:
        u.DE = datetime.now(UTC)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return err(500, 'Failed to update user', e)
    return jsonify({'message': 'User updated'}), 200


@CRUD.delete("/user/<uuid:ID>")
@require_admin
def delete_user(ID):
    if str(ID) in SYSTEM_USER_IDS:
        return err(403, 'Cannot delete system user')
    u = db.session.query(User).filter(User.id == ID).first()
    if not u:
        return nf_err("user", [])
    try:
        db.session.delete(u)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return err(500, 'Failed to delete user', e)
    return jsonify({'message': 'User deleted'}), 200


@CRUD.delete("/user/<uuid:ID>/mfa")
@require_admin
def admin_clear_user_mfa(ID):
    """Admin override: clear a user's 2FA secret (e.g. lost authenticator)."""
    u = db.session.query(User).filter(User.id == ID).first()
    if not u:
        return nf_err("user", [])
    if not u.MFA:
        return jsonify({'message': '2FA already disabled'}), 200
    u.MFA = None
    u.DE = datetime.now(UTC)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return err(500, 'Failed to clear MFA', e)
    return jsonify({'message': '2FA disabled'}), 200
