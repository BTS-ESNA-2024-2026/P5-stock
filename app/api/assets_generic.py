"""
API Générique de Gestion des Assets
Système EAV (Entity-Attribute-Value) pour gérer tous types d'assets
Supporte: weapons, ammo, vehicles, mre, pp
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.models.models import Asset, AssetType, Spec, Value, Room, Mission, User, Log
from app.utils.decorators import admin_required

bp = Blueprint('assets', __name__)


def get_asset_with_specs(db, asset):
    """Récupérer un asset avec toutes ses spécifications"""
    # Récupérer les valeurs des specs
    specs_values = {}
    values = db.query(Value).filter_by(asset_id=asset.id).all()

    for val in values:
        spec = db.query(Spec).filter_by(id=val.spec_id).first()
        if spec:
            specs_values[spec.name] = val.value

    # Récupérer les infos de localisation
    room = db.query(Room).filter_by(id=asset.room_id).first() if asset.room_id else None

    #  Récupérer le type d'asset
    asset_type = db.query(AssetType).filter_by(id=asset.type_asset_id).first()

    return {
        'id': asset.id,
        'nom': asset.nom,
        'number': asset.number,
        'status': asset.status,
        'type': asset_type.type if asset_type else None,
        'room': {
            'id': room.id,
            'building': room.building,
            'room': room.room
        } if room else None,
        'specs': specs_values,
        'valid_from': asset.DA.isoformat() if asset.DA else None,
        'valid_until': asset.DE.isoformat() if asset.DE else None,
        'exists': asset.exists
    }


@bp.route('/<asset_type>', methods=['GET'])
@jwt_required()
def list_assets(asset_type):
    """
    Lister tous les assets d'un type donné

    URL: /api/v1/assets/weapons, /api/v1/assets/ammo, etc.

    Query params:
        page: int (default 1)
        per_page: int (default 20)
        status: str (filter)
        room_id: int (filter)
        search: str (recherche par nom/number)
    """
    identity = get_jwt_identity()
    db = get_db()

    try:
        # Récupérer l'AssetType
        asset_type_obj = db.query(AssetType).filter_by(type=asset_type).first()
        if not asset_type_obj:
            return jsonify({'error': f'Type d\'asset inconnu: {asset_type}'}), 404

        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)

        # Filtres
        status = request.args.get('status')
        room_id = request.args.get('room_id', type=int)
        search = request.args.get('search')

        # Query
        query = db.query(Asset).filter_by(type_asset_id=asset_type_obj.id, exists=True)

        if status:
            query = query.filter(Asset.status == status)
        if room_id:
            query = query.filter(Asset.room_id == room_id)
        if search:
            query = query.filter(
                (Asset.nom.like(f'%{search}%')) |
                (Asset.number.like(f'%{search}%'))
            )

        # Compter le total
        total = query.count()

        # Paginer
        offset = (page - 1) * per_page
        assets = query.offset(offset).limit(per_page).all()

        # Formater
        assets_data = [get_asset_with_specs(db, asset) for asset in assets]

        return jsonify({
            'assets': assets_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200

    except SQLAlchemyError as e:
        current_app.logger.error(f'Erreur DB lors de la liste des assets: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/<asset_type>/<int:asset_id>', methods=['GET'])
@jwt_required()
def get_asset(asset_type, asset_id):
    """Récupérer les détails d'un asset spécifique"""
    db = get_db()

    try:
        asset = db.query(Asset).filter_by(id=asset_id, exists=True).first()

        if not asset:
            return jsonify({'error': 'Asset introuvable'}), 404

        asset_data = get_asset_with_specs(db, asset)

        return jsonify({'asset': asset_data}), 200

    except SQLAlchemyError as e:
        current_app.logger.error(f'Erreur DB lors de la récupération asset: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/<asset_type>', methods=['POST'])
@jwt_required()
def create_asset(asset_type):
    """
    Créer un nouvel asset

    Body:
        nom: str (required)
        number: str (required)
        room_id: int (required)
        status: str (optional, default AVAILABLE)
        specs: dict (optional, key-value pairs)
    """
    identity = get_jwt_identity()
    data = request.get_json()
    db = get_db()

    try:
        # Valider les champs requis
        if not data or not data.get('nom') or not data.get('number'):
            return jsonify({'error': 'Champs requis manquants: nom, number'}), 400

        # Récupérer l'AssetType
        asset_type_obj = db.query(AssetType).filter_by(type=asset_type).first()
        if not asset_type_obj:
            return jsonify({'error': f'Type d\'asset inconnu: {asset_type}'}), 404

        # Vérifier que le numéro n'existe pas déjà
        existing = db.query(Asset).filter_by(
            number=data['number'],
            type_asset_id=asset_type_obj.id,
            exists=True
        ).first()

        if existing:
            return jsonify({'error': 'Ce numéro existe déjà pour ce type d\'asset'}), 409

        # Créer l'asset
        new_asset = Asset(
            nom=data['nom'],
            number=data['number'],
            type_asset_id=asset_type_obj.id,
            added_by_id=identity['user_id'],
            room_id=data.get('room_id'),
            status=data.get('status', 'AVAILABLE'),
            DA=datetime.utcnow(),
            DE=datetime.utcnow() + timedelta(days=3650),  # 10 ans par défaut
            exists=True
        )

        db.add(new_asset)
        db.flush()

        # Ajouter les specs si fournies
        if 'specs' in data and isinstance(data['specs'], dict):
            specs = db.query(Spec).filter_by(type_id=asset_type_obj.id).all()
            specs_map = {spec.name: spec.id for spec in specs}

            for spec_name, spec_value in data['specs'].items():
                if spec_name in specs_map:
                    value_entry = Value(
                        asset_id=new_asset.id,
                        spec_id=specs_map[spec_name],
                        value=str(spec_value)
                    )
                    db.add(value_entry)

        # Logger l'action
        log_entry = Log(
            user_id=identity['user_id'],
            asset_id=new_asset.id,
            D=datetime.utcnow(),
            action='CREATE',
            desc=f'Création asset {asset_type}: {data["nom"]}'
        )
        db.add(log_entry)

        db.commit()

        current_app.logger.info(f'Asset créé: {asset_type}/{data["nom"]} par {identity["username"]}')

        asset_data = get_asset_with_specs(db, new_asset)

        return jsonify({
            'asset': asset_data,
            'message': 'Asset créé avec succès'
        }), 201

    except SQLAlchemyError as e:
        db.rollback()
        current_app.logger.error(f'Erreur DB lors de la création asset: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/<asset_type>/<int:asset_id>', methods=['PUT'])
@jwt_required()
def update_asset(asset_type, asset_id):
    """
    Mettre à jour un asset

    Body:
        nom: str (optional)
        status: str (optional)
        room_id: int (optional)
        specs: dict (optional)
    """
    identity = get_jwt_identity()
    data = request.get_json()
    db = get_db()

    try:
        asset = db.query(Asset).filter_by(id=asset_id, exists=True).first()

        if not asset:
            return jsonify({'error': 'Asset introuvable'}), 404

        # Mettre à jour les champs
        if 'nom' in data:
            asset.nom = data['nom']
        if 'status' in data:
            asset.status = data['status']
        if 'room_id' in data:
            asset.room_id = data['room_id']

        # Mettre à jour les specs
        if 'specs' in data and isinstance(data['specs'], dict):
            asset_type_obj = db.query(AssetType).filter_by(id=asset.type_asset_id).first()
            specs = db.query(Spec).filter_by(type_id=asset_type_obj.id).all()
            specs_map = {spec.name: spec.id for spec in specs}

            for spec_name, spec_value in data['specs'].items():
                if spec_name in specs_map:
                    # Chercher si la valeur existe déjà
                    existing_value = db.query(Value).filter_by(
                        asset_id=asset_id,
                        spec_id=specs_map[spec_name]
                    ).first()

                    if existing_value:
                        existing_value.value = str(spec_value)
                    else:
                        new_value = Value(
                            asset_id=asset_id,
                            spec_id=specs_map[spec_name],
                            value=str(spec_value)
                        )
                        db.add(new_value)

        # Logger
        log_entry = Log(
            user_id=identity['user_id'],
            asset_id=asset_id,
            D=datetime.utcnow(),
            action='UPDATE',
            desc=f'Modification asset {asset.nom}'
        )
        db.add(log_entry)

        db.commit()

        current_app.logger.info(f'Asset modifié: {asset.nom} par {identity["username"]}')

        asset_data = get_asset_with_specs(db, asset)

        return jsonify({
            'asset': asset_data,
            'message': 'Asset modifié avec succès'
        }), 200

    except SQLAlchemyError as e:
        db.rollback()
        current_app.logger.error(f'Erreur DB lors de la modification asset: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/<asset_type>/<int:asset_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_asset(asset_type, asset_id):
    """
    Supprimer (soft delete) un asset
    """
    identity = get_jwt_identity()
    db = get_db()

    try:
        asset = db.query(Asset).filter_by(id=asset_id).first()

        if not asset:
            return jsonify({'error': 'Asset introuvable'}), 404

        # Soft delete
        asset.exists = False

        # Logger
        log_entry = Log(
            user_id=identity['user_id'],
            asset_id=asset_id,
            D=datetime.utcnow(),
            action='DELETE',
            desc=f'Suppression asset {asset.nom}'
        )
        db.add(log_entry)

        db.commit()

        current_app.logger.info(f'Asset supprimé: {asset.nom} par {identity["username"]}')

        return jsonify({'message': 'Asset supprimé avec succès'}), 200

    except SQLAlchemyError as e:
        db.rollback()
        current_app.logger.error(f'Erreur DB lors de la suppression asset: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/types', methods=['GET'])
@jwt_required()
def list_asset_types():
    """Lister tous les types d'assets disponibles avec leurs specs"""
    db = get_db()

    try:
        asset_types = db.query(AssetType).all()

        types_data = []
        for at in asset_types:
            specs = db.query(Spec).filter_by(type_id=at.id).all()
            types_data.append({
                'id': at.id,
                'type': at.type,
                'specs': [{'id': s.id, 'name': s.name} for s in specs]
            })

        return jsonify({'asset_types': types_data}), 200

    except SQLAlchemyError as e:
        current_app.logger.error(f'Erreur DB lors de la liste des types: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()
