from datetime import datetime
from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Integer, SmallInteger, Text, String
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List


class Base(DeclarativeBase):
    pass


class Group(Base):
    __tablename__ = "group"
    __table_args__ = {"comment": "admin, user, viewer, technician"}

    id: Mapped[int] = mapped_column(
        SmallInteger, primary_key=True, autoincrement=True, comment="Group ID"
    )
    name: Mapped[str] = mapped_column(
        Text, nullable=False, comment="admin, user"
    )
    desc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    perms: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    users: Mapped[List["User"]] = relationship(back_populates="group")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    group_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("group.id"), nullable=False
    )
    DA: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    DE: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    username: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )
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
    group: Mapped["Group"] = relationship(back_populates="users")
    assets_added: Mapped[List["Asset"]] = relationship(
        back_populates="added_by", foreign_keys="Asset.added_by_id"
    )
    missions_created: Mapped[List["Mission"]] = relationship(
        back_populates="created_by"
    )
    admin_logs: Mapped[List["LogAdmin"]] = relationship(
        back_populates="admin", foreign_keys="LogAdmin.admin_id"
    )
    user_logs: Mapped[List["LogAdmin"]] = relationship(
        back_populates="user", foreign_keys="LogAdmin.user_id"
    )


class Base_(Base):
    __tablename__ = "base"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    rooms: Mapped[List["Room"]] = relationship(back_populates="base")


class Room(Base):
    __tablename__ = "room"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    building: Mapped[int] = mapped_column(
        Integer, ForeignKey("base.id"), nullable=False
    )
    room: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Paris"
    )

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

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    DA: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    DE: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    date_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    date_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    desc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Text, nullable=False, comment="finished, planned..."
    )
    theatre: Mapped[str] = mapped_column(
        Text, nullable=False, comment="location"
    )

    # Relationships
    created_by: Mapped["User"] = relationship(back_populates="missions_created")
    assets: Mapped[List["Asset"]] = relationship(back_populates="mission")
    logs: Mapped[List["LogMission"]] = relationship(back_populates="mission")


class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = {"comment": "in mission, on repair, available..."}

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="vehicle no 45, 12th HK 416...",
    )
    added_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
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
    nom: Mapped[str] = mapped_column(
        Text, nullable=False, comment="SN, PN, chassi no..."
    )
    number: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="MRE number 3574\nmay not be necessary"
    )
    status: Mapped[str] = mapped_column(Text, nullable=False)
    exists: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="discarded, destroyed, sold, or in stock",
    )
    shelf: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="shelf no 355"
    )

    # Relationships
    added_by: Mapped["User"] = relationship(
        back_populates="assets_added", foreign_keys=[added_by_id]
    )
    asset_type: Mapped["AssetType"] = relationship(back_populates="assets")
    mission: Mapped[Optional["Mission"]] = relationship(back_populates="assets")
    room: Mapped[Optional["Room"]] = relationship(back_populates="assets")
    values: Mapped[List["Value"]] = relationship(back_populates="asset")
    logs: Mapped[List["Log"]] = relationship(back_populates="asset")


class Spec(Base):
    __tablename__ = "specs"

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


class Value(Base):
    __tablename__ = "value"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="link between spec and asset by adding value : 3rd car's kilometers : 400000km",
    )
    asset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("assets.id"), nullable=False
    )
    spec_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("specs.id"), nullable=False
    )
    DA: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    DE: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    value: Mapped[str] = mapped_column(
        Text, nullable=False, comment="25000Km, m855 ball point..."
    )

    # Relationships
    asset: Mapped["Asset"] = relationship(back_populates="values")
    spec: Mapped["Spec"] = relationship(back_populates="values")


class LogAdmin(Base):
    __tablename__ = "log_admin"
    __table_args__ = {
        "comment": "separated admin logs for added security, when user (user_id) are edited/added... or when app settings are changed"
    }

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    admin_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    D: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    action: Mapped[str] = mapped_column(
        Text, nullable=False, comment="renamed john to martha"
    )
    desc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    admin: Mapped["User"] = relationship(
        back_populates="admin_logs", foreign_keys=[admin_id]
    )
    user: Mapped[Optional["User"]] = relationship(
        back_populates="user_logs", foreign_keys=[user_id]
    )


class Log(Base):
    __tablename__ = "log"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    asset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("assets.id"), nullable=False
    )
    D: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    action: Mapped[str] = mapped_column(
        Text, nullable=False, comment="added car #3\nchanged bullet 7's grammage value"
    )
    old_value: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    asset: Mapped["Asset"] = relationship(back_populates="logs")


class LogMission(Base):
    __tablename__ = "log_mission"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    mission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("mission.id"), nullable=False
    )
    D: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    action: Mapped[str] = mapped_column(
        Text, nullable=False, comment="changed date, removed description of mission..."
    )
    old_value: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    mission: Mapped["Mission"] = relationship(back_populates="logs")