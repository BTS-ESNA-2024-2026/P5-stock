from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.model import Base, Asset, Log
from datetime import datetime


class MySqlConnector:
    def __init__(self, server, databaseName, databaseUser, databasePassword):
        self.DATABASE_URL = f"mysql+pymysql://{databaseUser}:{databasePassword}@{server}/{databaseName}"
        self.engine = create_engine(self.DATABASE_URL)
        self.session = sessionmaker(bind=self.engine)()

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def close(self):
        self.session.close()

    # ============= ASSET METHODS =============

    def material_as_lost(self, asset_id: int, description: str = None) -> bool:
        """Marque un asset comme perdu."""
        asset = self.session.get(Asset, asset_id)
        if not asset or asset.status == "LOST":
            return False

        try:
            asset.status = "LOST"
            asset.DE = datetime.now()
            self.session.add(Log(asset_id=asset_id, D=datetime.now(), action="EDITED", description=description or "Status changed to LOST"))
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False
