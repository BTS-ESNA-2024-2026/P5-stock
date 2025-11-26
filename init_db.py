"""
Script d'initialisation de la base de données
Crée les tables et insert des données de test

Usage:
    python init_db.py
"""

import sys
from datetime import datetime, timedelta
from app.database import init_db, create_tables, get_db
from app.models.models import (
    Group, User, Base_, Room, AssetType, Spec, Mission, Asset, Value
)
from app.utils.password import hash_password
from flask import Flask


def create_app_context():
    """Créer un contexte Flask minimal pour l'initialisation"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret'
    app.config['DEBUG'] = True
    from app.config import DevelopmentConfig
    app.config.from_object(DevelopmentConfig)
    return app


def init_database():
    """Initialiser la base de données et créer les tables"""
    print("🔧 Initialisation de la connexion à la base de données...")
    app = create_app_context()

    with app.app_context():
        init_db(app)
        print("✅ Connexion établie")

        print("\n🔧 Création des tables...")
        create_tables()
        print("✅ Tables créées")

    return app


def create_default_groups(db):
    """Créer les groupes par défaut"""
    print("\n🔧 Création des groupes...")

    groups_data = [
        {
            'name': 'ADMIN',
            'desc': 'Administrateurs système - Accès complet',
            'perms': 'read:*,write:*,delete:*,admin:*'
        },
        {
            'name': 'USER',
            'desc': 'Utilisateurs standards - Accès en lecture/écriture',
            'perms': 'read:*,write:weapons,write:vehicles,write:missions'
        },
        {
            'name': 'READONLY',
            'desc': 'Utilisateurs en lecture seule',
            'perms': 'read:*'
        },
        {
            'name': 'MODERATOR',
            'desc': 'Modérateurs - Gestion des utilisateurs et validation',
            'perms': 'read:*,write:*,validate:*'
        }
    ]

    for group_data in groups_data:
        group = Group(**group_data)
        db.add(group)

    db.commit()
    print(f"✅ {len(groups_data)} groupes créés")


def create_default_users(db):
    """Créer des utilisateurs de test"""
    print("\n🔧 Création des utilisateurs...")

    # Récupérer les groupes
    admin_group = db.query(Group).filter_by(name='ADMIN').first()
    user_group = db.query(Group).filter_by(name='USER').first()
    readonly_group = db.query(Group).filter_by(name='READONLY').first()

    # Dates de validité
    now = datetime.utcnow()
    valid_from = now - timedelta(days=30)
    valid_until = now + timedelta(days=365)

    users_data = [
        {
            'username': 'admin',
            'name': 'Administrateur Principal',
            'password': 'Admin123!@#SecurePassword',
            'group_id': admin_group.id,
            'DA': valid_from,
            'DE': valid_until,
            'active': True,
            'MFA': None  # MFA non activé par défaut
        },
        {
            'username': 'logisticien',
            'name': 'Jean Dupont',
            'password': 'Logis123!@#SecurePassword',
            'group_id': user_group.id,
            'DA': valid_from,
            'DE': valid_until,
            'active': True,
            'MFA': None
        },
        {
            'username': 'viewer',
            'name': 'Marie Martin',
            'password': 'Viewer123!@#SecurePassword',
            'group_id': readonly_group.id,
            'DA': valid_from,
            'DE': valid_until,
            'active': True,
            'MFA': None
        }
    ]

    created_users = []
    for user_data in users_data:
        password = user_data.pop('password')
        hash_str, algorithm = hash_password(password)

        user = User(
            **user_data,
            hash=hash_str,
            hash_algorithm=algorithm
        )
        db.add(user)
        created_users.append({
            'username': user_data['username'],
            'password': password,
            'role': db.query(Group).get(user_data['group_id']).name
        })

    db.commit()

    print(f"✅ {len(users_data)} utilisateurs créés\n")
    print("📋 Credentials de test:")
    print("-" * 60)
    for user in created_users:
        print(f"  Username: {user['username']:<15} Password: {user['password']:<30} Role: {user['role']}")
    print("-" * 60)


def create_locations(db):
    """Créer les localisations (bases et salles)"""
    print("\n🔧 Création des localisations...")

    # Créer des bases
    bases_data = [
        {'name': 'Base Alpha', 'address': 'Paris, France'},
        {'name': 'Base Bravo', 'address': 'Lyon, France'},
        {'name': 'Base Charlie', 'address': 'Marseille, France'}
    ]

    for base_data in bases_data:
        base = Base_(**base_data)
        db.add(base)

    db.commit()

    # Créer des salles pour chaque base
    bases = db.query(Base_).all()
    rooms_count = 0

    for base in bases:
        rooms_data = [
            {'building': base.id, 'room': 'Armurerie A'},
            {'building': base.id, 'room': 'Armurerie B'},
            {'building': base.id, 'room': 'Garage véhicules'},
            {'building': base.id, 'room': 'Entrepôt munitions'},
            {'building': base.id, 'room': 'Stock rations'}
        ]

        for room_data in rooms_data:
            room = Room(**room_data)
            db.add(room)
            rooms_count += 1

    db.commit()
    print(f"✅ {len(bases_data)} bases et {rooms_count} salles créées")


def create_asset_types_and_specs(db):
    """Créer les types d'assets et leurs spécifications"""
    print("\n🔧 Création des types d'assets et spécifications...")

    asset_types_with_specs = [
        {
            'type': 'weapon',
            'specs': ['caliber', 'brand', 'model', 'last_revision', 'next_revision']
        },
        {
            'type': 'ammo',
            'specs': ['caliber', 'bullet_type', 'quantity', 'expiration_date', 'brand']
        },
        {
            'type': 'vehicle',
            'specs': ['brand', 'model', 'plate_number', 'chassis_number', 'kilometers', 'last_maintenance', 'next_maintenance']
        },
        {
            'type': 'mre',
            'specs': ['type', 'halal', 'vegetarian', 'allergens', 'expiration_date', 'quantity']
        },
        {
            'type': 'pp',
            'specs': ['type', 'size', 'certification', 'mandatory', 'expiration_date']
        }
    ]

    for asset_type_data in asset_types_with_specs:
        # Créer le type d'asset
        asset_type = AssetType(type=asset_type_data['type'])
        db.add(asset_type)
        db.flush()  # Pour obtenir l'ID

        # Créer les specs pour ce type
        for spec_name in asset_type_data['specs']:
            spec = Spec(type_id=asset_type.id, name=spec_name)
            db.add(spec)

    db.commit()
    print(f"✅ {len(asset_types_with_specs)} types d'assets avec spécifications créés")


def create_sample_assets(db):
    """Créer quelques assets d'exemple"""
    print("\n🔧 Création d'assets d'exemple...")

    # Récupérer les données nécessaires
    admin_user = db.query(User).filter_by(username='admin').first()
    weapon_type = db.query(AssetType).filter_by(type='weapon').first()
    vehicle_type = db.query(AssetType).filter_by(type='vehicle').first()
    room = db.query(Room).first()

    now = datetime.utcnow()

    # Créer quelques armes
    weapons_data = [
        {
            'nom': 'HK416-001',
            'number': '001',
            'status': 'AVAILABLE',
            'type_asset_id': weapon_type.id,
            'added_by_id': admin_user.id,
            'room_id': room.id,
            'DA': now,
            'DE': now + timedelta(days=3650),
            'exists': True
        },
        {
            'nom': 'HK416-002',
            'number': '002',
            'status': 'AVAILABLE',
            'type_asset_id': weapon_type.id,
            'added_by_id': admin_user.id,
            'room_id': room.id,
            'DA': now,
            'DE': now + timedelta(days=3650),
            'exists': True
        }
    ]

    # Créer quelques véhicules
    vehicles_data = [
        {
            'nom': 'VEHICULE-001',
            'number': 'VHL-001',
            'status': 'AVAILABLE',
            'type_asset_id': vehicle_type.id,
            'added_by_id': admin_user.id,
            'room_id': room.id,
            'DA': now,
            'DE': now + timedelta(days=3650),
            'exists': True
        }
    ]

    assets_count = 0
    for asset_data in weapons_data + vehicles_data:
        asset = Asset(**asset_data)
        db.add(asset)
        assets_count += 1

    db.commit()
    print(f"✅ {assets_count} assets d'exemple créés")


def main():
    """Fonction principale"""
    print("=" * 60)
    print("  INITIALISATION DE LA BASE DE DONNÉES SGLM")
    print("=" * 60)

    try:
        # Initialiser la DB et créer les tables
        app = init_database()

        with app.app_context():
            db = get_db()

            try:
                # Créer les données de test
                create_default_groups(db)
                create_default_users(db)
                create_locations(db)
                create_asset_types_and_specs(db)
                create_sample_assets(db)

                print("\n" + "=" * 60)
                print("✅ INITIALISATION TERMINÉE AVEC SUCCÈS!")
                print("=" * 60)
                print("\n🚀 Vous pouvez maintenant démarrer l'application:")
                print("   python main.py")
                print("\n📝 API Documentation: http://localhost:5000/api/v1")
                print("🔍 Health Check: http://localhost:5000/health\n")

            except Exception as e:
                db.rollback()
                print(f"\n❌ Erreur lors de la création des données: {str(e)}")
                import traceback
                traceback.print_exc()
                sys.exit(1)

            finally:
                db.close()

    except Exception as e:
        print(f"\n❌ Erreur lors de l'initialisation: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
