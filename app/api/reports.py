"""
Blueprint Rapports et Tableaux de Bord
[EF-901-P à EF-904-S] Tableaux de bord, KPI et rapports
Cas d'utilisation UC-05, UC-06
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

from app.database import get_db
from app.models.models import Asset, AssetType, Mission, User, Log

bp = Blueprint('reports', __name__)


@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Tableau de bord avec KPI en temps réel"""
    db = get_db()

    try:
        # Compter tous les assets par type et statut
        asset_types = db.query(AssetType).all()

        assets_summary = []
        for asset_type in asset_types:
            total = db.query(Asset).filter_by(type_asset_id=asset_type.id, exists=True).count()
            available = db.query(Asset).filter_by(type_asset_id=asset_type.id, status='AVAILABLE', exists=True).count()
            in_use = db.query(Asset).filter_by(type_asset_id=asset_type.id, status='IN_USE', exists=True).count()

            assets_summary.append({
                'type': asset_type.type,
                'total': total,
                'available': available,
                'in_use': in_use,
                'availability_rate': round((available / total * 100) if total > 0 else 0, 2)
            })

        # Missions actives
        active_missions = db.query(Mission).filter_by(status='ACTIVE').count()
        planned_missions = db.query(Mission).filter_by(status='PLANNED').count()

        # Activités récentes
        recent_logs = db.query(Log).order_by(Log.D.desc()).limit(10).all()

        recent_activity = [{
            'action': log.action,
            'description': log.desc,
            'date': log.D.isoformat() if log.D else None
        } for log in recent_logs]

        return jsonify({
            'dashboard': {
                'assets': assets_summary,
                'missions': {
                    'active': active_missions,
                    'planned': planned_missions
                },
                'recent_activity': recent_activity
            }
        }), 200

    finally:
        db.close()


@bp.route('/assets', methods=['GET'])
@jwt_required()
def get_assets_report():
    """Rapport détaillé des assets"""
    db = get_db()

    try:
        asset_type = request.args.get('type')
        status = request.args.get('status')

        query = db.query(Asset).filter_by(exists=True)

        if asset_type:
            at = db.query(AssetType).filter_by(type=asset_type).first()
            if at:
                query = query.filter(Asset.type_asset_id == at.id)

        if status:
            query = query.filter(Asset.status == status)

        assets = query.all()

        assets_data = [{
            'id': asset.id,
            'nom': asset.nom,
            'number': asset.number,
            'status': asset.status,
            'created': asset.DA.isoformat() if asset.DA else None
        } for asset in assets]

        return jsonify({
            'report': {
                'generated_at': datetime.utcnow().isoformat(),
                'total_count': len(assets_data),
                'assets': assets_data
            }
        }), 200

    finally:
        db.close()


@bp.route('/missions', methods=['GET'])
@jwt_required()
def get_missions_report():
    """Rapport des missions"""
    db = get_db()

    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = db.query(Mission)

        if start_date:
            query = query.filter(Mission.DS >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Mission.DE <= datetime.fromisoformat(end_date))

        missions = query.all()

        missions_data = [{
            'id': m.id,
            'name': m.name,
            'status': m.status,
            'start_date': m.DS.isoformat() if m.DS else None,
            'end_date': m.DE.isoformat() if m.DE else None,
            'assets_count': db.query(Asset).filter_by(mission_id=m.id).count()
        } for m in missions]

        return jsonify({
            'report': {
                'generated_at': datetime.utcnow().isoformat(),
                'total_missions': len(missions_data),
                'missions': missions_data
            }
        }), 200

    finally:
        db.close()


@bp.route('/activity', methods=['GET'])
@jwt_required()
def get_activity_report():
    """Rapport d'activité"""
    identity = get_jwt_identity()
    db = get_db()

    try:
        if identity['role'] not in ['ADMIN', 'MODERATOR']:
            return jsonify({'error': 'Permission refusée'}), 403

        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)

        logs = db.query(Log).filter(Log.D >= start_date).all()

        # Grouper par action
        action_counts = {}
        for log in logs:
            action = log.action
            if action not in action_counts:
                action_counts[action] = 0
            action_counts[action] += 1

        return jsonify({
            'report': {
                'period_days': days,
                'total_actions': len(logs),
                'actions_by_type': action_counts
            }
        }), 200

    finally:
        db.close()
