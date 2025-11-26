"""
Blueprint Gestion des Missions
[EF-701-P à EF-706-I] Gestion des opérations logistiques
Cas d'utilisation UC-04
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.models.models import Mission, Asset, User, LogMission
from app.utils.decorators import admin_required

bp = Blueprint('missions', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def list_missions():
    """Lister toutes les missions"""
    db = get_db()

    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')

        query = db.query(Mission)
        if status:
            query = query.filter(Mission.status == status)

        total = query.count()
        missions = query.offset((page - 1) * per_page).limit(per_page).all()

        missions_data = [{
            'id': m.id,
            'name': m.name,
            'description': m.desc,
            'status': m.status,
            'start_date': m.DS.isoformat() if m.DS else None,
            'end_date': m.DE.isoformat() if m.DE else None,
            'assets_count': db.query(Asset).filter_by(mission_id=m.id).count()
        } for m in missions]

        return jsonify({
            'missions': missions_data,
            'pagination': {'page': page, 'per_page': per_page, 'total': total, 'pages': (total + per_page - 1) // per_page}
        }), 200

    finally:
        db.close()


@bp.route('/<int:mission_id>', methods=['GET'])
@jwt_required()
def get_mission(mission_id):
    """Récupérer les détails d'une mission"""
    db = get_db()

    try:
        mission = db.query(Mission).filter_by(id=mission_id).first()
        if not mission:
            return jsonify({'error': 'Mission introuvable'}), 404

        assets = db.query(Asset).filter_by(mission_id=mission_id).all()

        return jsonify({
            'mission': {
                'id': mission.id,
                'name': mission.name,
                'description': mission.desc,
                'status': mission.status,
                'start_date': mission.DS.isoformat() if mission.DS else None,
                'end_date': mission.DE.isoformat() if mission.DE else None,
                'assets': [{'id': a.id, 'nom': a.nom, 'number': a.number, 'status': a.status} for a in assets]
            }
        }), 200

    finally:
        db.close()


@bp.route('', methods=['POST'])
@jwt_required()
def create_mission():
    """Créer une nouvelle mission"""
    identity = get_jwt_identity()
    data = request.get_json()
    db = get_db()

    try:
        if not data or not data.get('name'):
            return jsonify({'error': 'Nom de mission requis'}), 400

        new_mission = Mission(
            name=data['name'],
            desc=data.get('description', ''),
            status=data.get('status', 'PLANNED'),
            DS=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
            DE=datetime.fromisoformat(data['end_date']) if data.get('end_date') else None
        )

        db.add(new_mission)
        db.flush()

        log_entry = LogMission(mission_id=new_mission.id, user_id=identity['user_id'], D=datetime.utcnow(), action='CREATE', desc=f'Mission créée: {data["name"]}')
        db.add(log_entry)
        db.commit()

        return jsonify({'mission': {'id': new_mission.id, 'name': new_mission.name, 'status': new_mission.status}, 'message': 'Mission créée avec succès'}), 201

    except SQLAlchemyError as e:
        db.rollback()
        current_app.logger.error(f'Erreur DB: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/<int:mission_id>', methods=['PUT'])
@jwt_required()
def update_mission(mission_id):
    """Mettre à jour une mission"""
    identity = get_jwt_identity()
    data = request.get_json()
    db = get_db()

    try:
        mission = db.query(Mission).filter_by(id=mission_id).first()
        if not mission:
            return jsonify({'error': 'Mission introuvable'}), 404

        if 'name' in data:
            mission.name = data['name']
        if 'description' in data:
            mission.desc = data['description']
        if 'status' in data:
            mission.status = data['status']
        if 'start_date' in data:
            mission.DS = datetime.fromisoformat(data['start_date'])
        if 'end_date' in data:
            mission.DE = datetime.fromisoformat(data['end_date'])

        log_entry = LogMission(mission_id=mission_id, user_id=identity['user_id'], D=datetime.utcnow(), action='UPDATE', desc='Mission modifiée')
        db.add(log_entry)
        db.commit()

        return jsonify({'message': 'Mission modifiée avec succès'}), 200

    except SQLAlchemyError as e:
        db.rollback()
        current_app.logger.error(f'Erreur DB: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/<int:mission_id>/assign', methods=['POST'])
@jwt_required()
def assign_assets(mission_id):
    """Assigner des assets à une mission"""
    identity = get_jwt_identity()
    data = request.get_json()
    db = get_db()

    try:
        mission = db.query(Mission).filter_by(id=mission_id).first()
        if not mission:
            return jsonify({'error': 'Mission introuvable'}), 404

        if not data or not data.get('asset_ids'):
            return jsonify({'error': 'Liste des assets requis'}), 400

        assigned_count = 0
        for asset_id in data['asset_ids']:
            asset = db.query(Asset).filter_by(id=asset_id).first()
            if asset and asset.status == 'AVAILABLE':
                asset.mission_id = mission_id
                asset.status = 'IN_USE'
                assigned_count += 1

        log_entry = LogMission(mission_id=mission_id, user_id=identity['user_id'], D=datetime.utcnow(), action='ASSIGN_ASSETS', desc=f'{assigned_count} assets assignés')
        db.add(log_entry)
        db.commit()

        return jsonify({'message': f'{assigned_count} assets assignés', 'assigned_count': assigned_count}), 200

    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/<int:mission_id>/unassign', methods=['POST'])
@jwt_required()
def unassign_assets(mission_id):
    """Retirer des assets d'une mission"""
    identity = get_jwt_identity()
    data = request.get_json()
    db = get_db()

    try:
        unassigned_count = 0
        for asset_id in data.get('asset_ids', []):
            asset = db.query(Asset).filter_by(id=asset_id, mission_id=mission_id).first()
            if asset:
                asset.mission_id = None
                asset.status = 'AVAILABLE'
                unassigned_count += 1

        log_entry = LogMission(mission_id=mission_id, user_id=identity['user_id'], D=datetime.utcnow(), action='UNASSIGN_ASSETS', desc=f'{unassigned_count} assets retirés')
        db.add(log_entry)
        db.commit()

        return jsonify({'message': f'{unassigned_count} assets retirés', 'unassigned_count': unassigned_count}), 200

    finally:
        db.close()
