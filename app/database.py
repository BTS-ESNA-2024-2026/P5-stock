"""
Gestion de la connexion à la base de données
Configuration SQLAlchemy pour MySQL
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
import os

from app.models.models import Base

# Engine SQLAlchemy
engine = None
SessionLocal = None


def init_db(app):
    """
    Initialise la connexion à la base de données

    Args:
        app: Instance Flask
    """
    global engine, SessionLocal

    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        raise ValueError("DATABASE_URL n'est pas définie dans les variables d'environnement")

    # Créer l'engine avec pool de connexions
    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Vérifie que la connexion est vivante
        pool_recycle=3600,   # Recycle les connexions après 1h
        echo=app.config['DEBUG']  # Log SQL en mode debug
    )

    # Créer une session factory thread-safe
    SessionLocal = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )

    # Ajouter la session à l'app context
    app.db_session = SessionLocal

    app.logger.info(f"Database initialized: {database_url.split('@')[1]}")


def create_tables():
    """
    Crée toutes les tables dans la base de données
    À utiliser uniquement pour l'initialisation initiale
    """
    if engine is None:
        raise ValueError("Database engine not initialized. Call init_db() first.")

    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Supprime toutes les tables (DANGER! À utiliser avec précaution)
    """
    if engine is None:
        raise ValueError("Database engine not initialized. Call init_db() first.")

    Base.metadata.drop_all(bind=engine)


def get_db():
    """
    Obtenir une session de base de données
    À utiliser dans les routes Flask

    Usage:
        db = get_db()
        try:
            # Faire des opérations
            user = db.query(User).first()
            db.commit()
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()

    Returns:
        Session SQLAlchemy
    """
    if SessionLocal is None:
        raise ValueError("Database not initialized. Call init_db() first.")

    return SessionLocal()


def close_db(e=None):
    """
    Ferme la session de base de données
    À appeler à la fin de chaque requête
    """
    if SessionLocal is not None:
        SessionLocal.remove()
