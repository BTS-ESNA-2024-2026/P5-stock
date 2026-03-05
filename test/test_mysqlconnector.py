import pytest
from datetime import datetime
from uuid import UUID

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from database.model import Base, Asset, AssetType, Log
from utils.mysqlconnector import DbConnector
from uuid_extensions import uuid7


@pytest.fixture
def db():
    connector = DbConnector.__new__(DbConnector)
    connector.engine = create_engine("sqlite:///:memory:")

    # SQLite doesn't support native UUID, so we need to handle UUID as strings
    @event.listens_for(connector.engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.close()

    connector.session = sessionmaker(bind=connector.engine)()
    Base.metadata.create_all(connector.engine)

    asset_type_id = uuid7()
    asset_id = uuid7()
    connector.session.add(AssetType(id=asset_type_id, type="Vehicle"))
    connector.session.add(Asset(id=asset_id, type_asset_id=asset_type_id, DA=datetime.now(), DE=datetime.now(), name="Test", status="STOCK"))
    connector.session.commit()

    connector._test_asset_id = asset_id
    yield connector

    connector.session.close()


def test_material_as_lost(db):
    asset_id = db._test_asset_id
    assert db.material_as_lost(asset_id, "Perdu") is True
    assert db.session.get(Asset, asset_id).status == "LOST"
    assert len(db.session.query(Log).filter_by(asset_id=asset_id).all()) == 1
