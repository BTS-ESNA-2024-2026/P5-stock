from datetime import UTC, datetime

from sqlalchemy import event, inspect
from uuid_extensions import uuid7

from src.database.model import (
    Asset,
    Log,
    LogAdmin,
    LogMission,
    Mission,
    Spec,
    User,
    Value,
)

# ============================================================================
# AUDIT EVENT LISTENERS
# ============================================================================

# --- Asset -------------------------------------------------------------------

@event.listens_for(Asset, 'after_insert')
def _asset_after_insert(mapper, connection, target):
    connection.execute(Log.__table__.insert().values(
        id=uuid7(), asset_id=target.id, D=datetime.now(UTC),
        action='CREATED',
        description=f'Asset created: {target.name} (Type: {target.type_asset_id}, Status: {target.status})',
    ))


@event.listens_for(Asset, 'after_update')
def _asset_after_update(mapper, connection, target):
    state = inspect(target)
    changes = []

    for attr, label in [('name', 'Name'), ('status', 'Status')]:
        hist = state.attrs[attr].history
        if hist.has_changes() and hist.deleted:
            changes.append(f'{label}: "{hist.deleted[0]}" -> "{getattr(target, attr)}"')

    for attr, label in [('mission_id', 'Mission'), ('room_id', 'Room')]:
        hist = state.attrs[attr].history
        if hist.has_changes():
            old = hist.deleted[0] if hist.deleted else None
            new = getattr(target, attr)
            if old is None and new is not None:
                changes.append(f'{label} assigned: {new}')
            elif old is not None and new is None:
                changes.append(f'{label} removed: {old}')
            elif old != new:
                changes.append(f'{label}: {old} -> {new}')

    for attr, label in [('quantity', 'Quantity'), ('shelf', 'Shelf'), ('sensible', 'Sensible')]:
        hist = state.attrs[attr].history
        if hist.has_changes() and hist.deleted:
            old = hist.deleted[0] if hist.deleted[0] is not None else 'NULL'
            new = getattr(target, attr) if getattr(target, attr) is not None else 'NULL'
            changes.append(f'{label}: {old} -> {new}')

    if changes:
        connection.execute(Log.__table__.insert().values(
            id=uuid7(), asset_id=target.id, D=datetime.now(UTC),
            action='EDITED', description='; '.join(changes),
        ))


@event.listens_for(Asset, 'after_delete')
def _asset_after_delete(mapper, connection, target):
    connection.execute(Log.__table__.insert().values(
        id=uuid7(), asset_id=target.id, D=datetime.now(UTC),
        action='DELETED',
        description=f'Asset deleted: {target.name} (Type: {target.type_asset_id}, Status: {target.status})',
    ))


# --- Value -------------------------------------------------------------------

@event.listens_for(Value, 'after_insert')
def _value_after_insert(mapper, connection, target):
    connection.execute(Log.__table__.insert().values(
        id=uuid7(), asset_id=target.asset_id, spec_id=target.spec_id,
        value_id=target.id, D=datetime.now(UTC),
        action='CREATED',
        description=f'Value created for asset {target.asset_id}, spec {target.spec_id}: "{target.value}"',
    ))


@event.listens_for(Value, 'after_update')
def _value_after_update(mapper, connection, target):
    hist = inspect(target).attrs.value.history
    if hist.has_changes() and hist.deleted:
        connection.execute(Log.__table__.insert().values(
            id=uuid7(), asset_id=target.asset_id, spec_id=target.spec_id,
            value_id=target.id, D=datetime.now(UTC),
            action='EDITED',
            description=f'Value updated for asset {target.asset_id}, spec {target.spec_id}: "{hist.deleted[0]}" -> "{target.value}"',
        ))


@event.listens_for(Value, 'after_delete')
def _value_after_delete(mapper, connection, target):
    connection.execute(Log.__table__.insert().values(
        id=uuid7(), asset_id=target.asset_id, spec_id=target.spec_id,
        value_id=target.id, D=datetime.now(UTC),
        action='DELETED',
        description=f'Value deleted for asset {target.asset_id}, spec {target.spec_id}: "{target.value}"',
    ))


# --- Spec --------------------------------------------------------------------

@event.listens_for(Spec, 'after_insert')
def _spec_after_insert(mapper, connection, target):
    connection.execute(Log.__table__.insert().values(
        id=uuid7(), spec_id=target.id, D=datetime.now(UTC),
        action='CREATED',
        description=f'Spec created: {target.name} (Type: {target.type_id})',
    ))


@event.listens_for(Spec, 'after_update')
def _spec_after_update(mapper, connection, target):
    state = inspect(target)
    changes = []
    for attr, label in [('name', 'Name'), ('type_id', 'Type')]:
        hist = state.attrs[attr].history
        if hist.has_changes() and hist.deleted:
            changes.append(f'{label}: "{hist.deleted[0]}" -> "{getattr(target, attr)}"')
    if changes:
        connection.execute(Log.__table__.insert().values(
            id=uuid7(), spec_id=target.id, D=datetime.now(UTC),
            action='EDITED', description='; '.join(changes),
        ))


@event.listens_for(Spec, 'after_delete')
def _spec_after_delete(mapper, connection, target):
    connection.execute(Log.__table__.insert().values(
        id=uuid7(), spec_id=target.id, D=datetime.now(UTC),
        action='DELETED',
        description=f'Spec deleted: {target.name} (Type: {target.type_id})',
    ))


# --- User --------------------------------------------------------------------

@event.listens_for(User, 'after_insert')
def _user_after_insert(mapper, connection, target):
    connection.execute(LogAdmin.__table__.insert().values(
        id=uuid7(), user_id=target.id, D=datetime.now(UTC),
        action='CREATED',
        desc=f'User created: {target.username} (Group: {target.group_id})',
    ))


@event.listens_for(User, 'after_update')
def _user_after_update(mapper, connection, target):
    state = inspect(target)
    changes = []
    action = 'EDITED'

    active_hist = state.attrs['active'].history
    if active_hist.has_changes() and active_hist.deleted:
        old_active = active_hist.deleted[0]
        if old_active is True and target.active is False:
            action = 'DEACTIVATED'
            changes.append(f'User deactivated: {target.username}')
        elif old_active is False and target.active is True:
            action = 'ACTIVATED'
            changes.append(f'User activated: {target.username}')

    if action == 'EDITED':
        for attr, label in [('username', 'Username'), ('name', 'Name')]:
            hist = state.attrs[attr].history
            if hist.has_changes() and hist.deleted:
                old = hist.deleted[0] or ''
                changes.append(f'{label}: "{old}" -> "{getattr(target, attr) or ""}"')

        hist = state.attrs['group_id'].history
        if hist.has_changes() and hist.deleted:
            changes.append(f'Group: {hist.deleted[0]} -> {target.group_id}')

        hist = state.attrs['hash'].history
        if hist.has_changes() and hist.deleted:
            changes.append('Password changed')

        hist = state.attrs['MFA'].history
        if hist.has_changes():
            if target.MFA:
                changes.append('MFA enabled')
            else:
                changes.append('MFA disabled')

    if changes:
        connection.execute(LogAdmin.__table__.insert().values(
            id=uuid7(), user_id=target.id, D=datetime.now(UTC),
            action=action, desc='; '.join(changes),
        ))


@event.listens_for(User, 'after_delete')
def _user_after_delete(mapper, connection, target):
    connection.execute(LogAdmin.__table__.insert().values(
        id=uuid7(), user_id=target.id, D=datetime.now(UTC),
        action='DELETED',
        desc=f'User deleted: {target.username} (Group: {target.group_id})',
    ))


# --- Mission -----------------------------------------------------------------

@event.listens_for(Mission, 'after_insert')
def _mission_after_insert(mapper, connection, target):
    connection.execute(LogMission.__table__.insert().values(
        id=uuid7(), mission_id=target.id, D=datetime.now(UTC),
        action='CREATED',
        description=f'Mission created: {target.title} (Theatre: {target.theatre}, Status: {target.status})',
    ))


@event.listens_for(Mission, 'after_update')
def _mission_after_update(mapper, connection, target):
    state = inspect(target)
    changes = []

    for attr, label in [('title', 'Title'), ('status', 'Status'), ('theatre', 'Theatre')]:
        hist = state.attrs[attr].history
        if hist.has_changes() and hist.deleted:
            changes.append(f'{label}: "{hist.deleted[0]}" -> "{getattr(target, attr)}"')

    hist = state.attrs['description'].history
    if hist.has_changes():
        changes.append('Description changed')

    for attr, label in [('date_start', 'Start date'), ('date_end', 'End date')]:
        hist = state.attrs[attr].history
        if hist.has_changes():
            old = hist.deleted[0] if hist.deleted else None
            new = getattr(target, attr)
            if old is None and new is not None:
                changes.append(f'{label} set: {new}')
            elif old is not None and new is None:
                changes.append(f'{label} removed')
            elif old != new:
                changes.append(f'{label}: {old} -> {new}')

    if changes:
        connection.execute(LogMission.__table__.insert().values(
            id=uuid7(), mission_id=target.id, D=datetime.now(UTC),
            action='EDITED', description='; '.join(changes),
        ))


@event.listens_for(Mission, 'after_delete')
def _mission_after_delete(mapper, connection, target):
    connection.execute(LogMission.__table__.insert().values(
        id=uuid7(), mission_id=target.id, D=datetime.now(UTC),
        action='DELETED',
        description=f'Mission deleted: {target.title} (Theatre: {target.theatre}, Status: {target.status})',
    ))


# ============================================================================
# LOG PROTECTION  (prevents update/delete on log tables)
# ============================================================================

def _prevent_modify(mapper, connection, target):
    raise RuntimeError('Interdit: les logs ne peuvent pas etre modifies ou supprimes')


for _cls in (Log, LogAdmin, LogMission):
    event.listen(_cls, 'before_delete', _prevent_modify)
    event.listen(_cls, 'before_update', _prevent_modify)
