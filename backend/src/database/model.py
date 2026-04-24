from datetime import datetime
from typing import List, Optional
from uuid import UUID

from argon2 import PasswordHasher
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_extensions import uuid7

db = SQLAlchemy()
migrate = Migrate()
ph = PasswordHasher()


class Role(db.Model):  # noqa: F811
    __tablename__ = "role"
    __table_args__ = {"comment": "admin, user, viewer, technician"}

    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid7
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, comment="admin, user")
    desc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    perms: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Relationships
    users: Mapped[List["User"]] = relationship(back_populates="role")


class User(db.Model):  # noqa: F811
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    group_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("role.id"), nullable=False
    )
    DA: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    DE: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hash: Mapped[str] = mapped_column(
        Text, nullable=False, comment="1945B09A02C889190B3"
    )
    hash_algorithm: Mapped[str] = mapped_column(
        Text, nullable=False, comment="algo_rounds\nARGON2_32"
    )
    MFA: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="seed of MFA"
    )

    # Relationships
    role: Mapped["Role"] = relationship(back_populates="users")
    admin_logs: Mapped[List["LogAdmin"]] = relationship(
        back_populates="user", foreign_keys="LogAdmin.user_id"
    )

    def __init__(self, username: str, group_id,
        hash: str, hash_algorithm: str, name: Optional[str] = None,
        MFA: Optional[str] = None, active: bool = True):
        self.id = uuid7()
        self.username = username
        self.group_id = group_id
        self.DA = datetime.utcnow()
        self.DE = datetime.utcnow()
        self.hash = hash
        self.hash_algorithm = hash_algorithm
        self.name = name
        self.MFA = MFA
        self.active = active


class Base_(db.Model):  # noqa: F811
    __tablename__ = "base"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    rooms: Mapped[List["Room"]] = relationship(back_populates="base")


class Room(db.Model):  # noqa: F811
    __tablename__ = "room"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    base_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("base.id"), nullable=False
    )
    room: Mapped[str] = mapped_column(Text, nullable=False, comment="Paris")

    # Relationships
    base: Mapped["Base_"] = relationship(back_populates="rooms")
    assets: Mapped[List["Asset"]] = relationship(back_populates="room")


class AssetType(db.Model):  # noqa: F811
    __tablename__ = "asset_type"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid7,
        comment="vehicle, MRE, weapon...",
    )
    type: Mapped[str] = mapped_column(
        Text, nullable=False, comment="vehicle, MRE, weapon..."
    )

    # Relationships
    assets: Mapped[List["Asset"]] = relationship(back_populates="asset_type")
    specs: Mapped[List["Spec"]] = relationship(back_populates="asset_type")


class Mission(db.Model):  # noqa: F811
    __tablename__ = "mission"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    DA: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    DE: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    date_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    date_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Text, nullable=False, comment="finished, planned..."
    )
    theatre: Mapped[str] = mapped_column(Text, nullable=False, comment="location")

    # Relationships
    assets: Mapped[List["Asset"]] = relationship(back_populates="mission")
    logs: Mapped[List["LogMission"]] = relationship(back_populates="mission")


class Asset(db.Model):  # noqa: F811
    __tablename__ = "asset"
    __table_args__ = {"comment": "in mission, on repair, available..."}

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid7,
        comment="vehicle no 45, 12th HK 416...",
    )
    type_asset_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("asset_type.id"), nullable=False
    )
    mission_id: Mapped[Optional[UUID]] = mapped_column(
        Uuid,
        ForeignKey("mission.id"),
        nullable=True,
        comment="no assigned mission if value not assigned",
    )
    room_id: Mapped[Optional[UUID]] = mapped_column(
        Uuid, ForeignKey("room.id"), nullable=True
    )
    DA: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    DE: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    name: Mapped[str] = mapped_column(
        Text, nullable=False, comment="SN, PN, chassi no..."
    )
    number: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="MRE number 3574\nmay not be necessary, depends"
    )
    status: Mapped[str] = mapped_column(
        Enum('STOCK', 'DESTROYED', 'SOLD', 'LOST', 'TRANSIT', 'PURCHASED', name='asset_status'),
        nullable=False
    )
    quantity: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="for packs, do not set if quantity = 1 like for a vehicle",
    )
    shelf: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="shelf no 355"
    )
    sensible: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Relationships
    asset_type: Mapped["AssetType"] = relationship(back_populates="assets")
    mission: Mapped[Optional["Mission"]] = relationship(back_populates="assets")
    room: Mapped[Optional["Room"]] = relationship(back_populates="assets")
    values: Mapped[List["Value"]] = relationship(back_populates="asset")
    logs: Mapped[List["Log"]] = relationship(back_populates="asset")


class Spec(db.Model):  # noqa: F811
    __tablename__ = "spec"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid7,
        comment="specs #7 = how much km a car has",
    )
    type_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("asset_type.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(
        Text, nullable=False, comment="km, expiration date, bullet..."
    )

    # Relationships
    asset_type: Mapped["AssetType"] = relationship(back_populates="specs")
    values: Mapped[List["Value"]] = relationship(back_populates="spec")
    logs: Mapped[List["Log"]] = relationship(back_populates="spec")


class Value(db.Model):  # noqa: F811
    __tablename__ = "value"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid7,
        comment="link between spec and asset by adding value : 3rd car's kilometers : 400000km",
    )
    asset_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("asset.id"), nullable=False
    )
    spec_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("spec.id"), nullable=False
    )
    DA: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    DE: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    value: Mapped[str] = mapped_column(
        Text, nullable=False, comment="25000Km, m855 ball point..."
    )

    # Relationships
    asset: Mapped["Asset"] = relationship(back_populates="values")
    spec: Mapped["Spec"] = relationship(back_populates="values")
    logs: Mapped[List["Log"]] = relationship(back_populates="value")


class LogAdmin(db.Model):  # noqa: F811
    __tablename__ = "log_admin"
    __table_args__ = {
        "comment": "separated admin logs for added security, when user (user_id) are edited/added... or when app settings are changed"
    }

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("user.id"), nullable=False
    )
    D: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    action: Mapped[str] = mapped_column(
        Enum('CREATED', 'DELETED', 'EDITED', 'DEACTIVATED', 'ACTIVATED', name='log_admin_action'),
        nullable=False,
        comment="renamed john to martha",
    )
    desc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(
        back_populates="admin_logs", foreign_keys=[user_id]
    )


class Log(db.Model):  # noqa: F811
    __tablename__ = "log"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    asset_id: Mapped[Optional[UUID]] = mapped_column(
        Uuid, ForeignKey("asset.id"), nullable=True
    )
    spec_id: Mapped[Optional[UUID]] = mapped_column(
        Uuid, ForeignKey("spec.id"), nullable=True
    )
    value_id: Mapped[Optional[UUID]] = mapped_column(
        Uuid, ForeignKey("value.id"), nullable=True
    )
    D: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    action: Mapped[str] = mapped_column(
        Enum('CREATED', 'DELETED', 'EDITED', name='log_action'),
        nullable=False,
        comment="added car #3\nchanged bullet 7's grammage value",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="added helicopter 7's kilometers"
    )

    # Relationships
    asset: Mapped[Optional["Asset"]] = relationship(back_populates="logs")
    spec: Mapped[Optional["Spec"]] = relationship(back_populates="logs")
    value: Mapped[Optional["Value"]] = relationship(back_populates="logs")


class LogMission(db.Model):  # noqa: F811
    __tablename__ = "log_mission"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    mission_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("mission.id"), nullable=False
    )
    D: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    action: Mapped[str] = mapped_column(
        Enum('CREATED', 'DELETED', 'EDITED', name='log_mission_action'),
        nullable=False,
        comment="changed date, removed description of mission...",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment='"changed value x from z to y"'
    )

    # Relationships
    mission: Mapped["Mission"] = relationship(back_populates="logs")
