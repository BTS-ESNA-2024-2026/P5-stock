import uuid
from datetime import datetime

from argon2 import PasswordHasher
from sqlalchemy import (
    Boolean, DateTime, Enum, ForeignKey, Integer, SmallInteger, Text, String, BigInteger
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
ph = PasswordHasher()

class Base(DeclarativeBase):
    pass


class Role(Base):
    __tablename__ = "role"
    __table_args__ = {"comment": "admin, user, viewer, technician"}

    id: Mapped[int] = mapped_column(
        SmallInteger, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, comment="admin, user")
    desc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    perms: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Relationships
    users: Mapped[List["User"]] = relationship(back_populates="role")


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    group_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("role.id"), nullable=False
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

    def __init__(self, username: str, group_id: int,
        hash: str, hash_algorithm: str, name: Optional[str] = None,
        MFA: Optional[str] = None, active: bool = True):
        self.id = uuid.uuid4().int & ((1 << 63) - 1)
        self.username = username
        self.group_id = group_id
        self.DA = datetime.utcnow()
        self.DE = datetime.utcnow()
        self.hash = hash
        self.hash_algorithm = hash_algorithm
        self.name = name
        self.MFA = MFA
        self.active = active


class Base_(Base):
    __tablename__ = "base"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    rooms: Mapped[List["Room"]] = relationship(back_populates="base")


class Room(Base):
    __tablename__ = "room"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    base_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("base.id"), nullable=False
    )
    room: Mapped[str] = mapped_column(Text, nullable=False, comment="Paris")

    # Relationships
    base: Mapped["Base_"] = relationship(back_populates="rooms")
    assets: Mapped[List["Asset"]] = relationship(back_populates="room")


class AssetType(Base):
    __tablename__ = "asset_type"

    id: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True,
        autoincrement=True,
        comment="vehicle, MRE, weapon...",
    )
    type: Mapped[str] = mapped_column(
        Text, nullable=False, comment="vehicle, MRE, weapon..."
    )

    # Relationships
    assets: Mapped[List["Asset"]] = relationship(back_populates="asset_type")
    specs: Mapped[List["Spec"]] = relationship(back_populates="asset_type")


class Mission(Base):
    __tablename__ = "mission"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
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


class Asset(Base):
    __tablename__ = "asset"
    __table_args__ = {"comment": "in mission, on repair, available..."}

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="vehicle no 45, 12th HK 416...",
    )
    type_asset_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("asset_type.id"), nullable=False
    )
    mission_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("mission.id"),
        nullable=True,
        comment="no assigned mission if value not assigned",
    )
    room_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("room.id"), nullable=True
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
        Integer,
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


class Spec(Base):
    __tablename__ = "spec"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="specs #7 = how much km a car has",
    )
    type_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("asset_type.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(
        Text, nullable=False, comment="km, expiration date, bullet..."
    )

    # Relationships
    asset_type: Mapped["AssetType"] = relationship(back_populates="specs")
    values: Mapped[List["Value"]] = relationship(back_populates="spec")
    logs: Mapped[List["Log"]] = relationship(back_populates="spec")


class Value(Base):
    __tablename__ = "value"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="link between spec and asset by adding value : 3rd car's kilometers : 400000km",
    )
    asset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("asset.id"), nullable=False
    )
    spec_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("spec.id"), nullable=False
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


class LogAdmin(Base):
    __tablename__ = "log_admin"
    __table_args__ = {
        "comment": "separated admin logs for added security, when user (user_id) are edited/added... or when app settings are changed"
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("user.id"), nullable=False
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


class Log(Base):
    __tablename__ = "log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("asset.id"), nullable=True
    )
    spec_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("spec.id"), nullable=True
    )
    value_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("value.id"), nullable=True
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


class LogMission(Base):
    __tablename__ = "log_mission"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("mission.id"), nullable=False
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