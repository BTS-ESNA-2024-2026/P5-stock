import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.model import Base, Asset, AssetType, Log
from utils.mysqlconnector import MySqlConnector


@pytest.fixture
def db():
    connector = MySqlConnector.__new__(MySqlConnector)
    connector.engine = create_engine("sqlite:///:memory:")
    connector.session = sessionmaker(bind=connector.engine)()
    Base.metadata.create_all(connector.engine)

    connector.session.add(AssetType(id=1, type="Vehicle"))
    connector.session.add(Asset(id=1, type_asset_id=1, DA=datetime.now(), DE=datetime.now(), name="Test", status="STOCK"))
    connector.session.commit()

    yield connector

    connector.session.close()


def test_material_as_lost(db):
    assert db.material_as_lost(1, "Perdu") is True
    assert db.session.get(Asset, 1).status == "LOST"
    assert len(db.session.query(Log).filter_by(asset_id=1).all()) == 1
