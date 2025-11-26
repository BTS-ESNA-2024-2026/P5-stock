"""
Blueprint Gestion des Logs et Audit
[EF-801-P à EF-805-I] Logs et traçabilité
Cas d'utilisation UC-09
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.models.models import Log, LogAdmin, LogMission, User, Asset

bp = Blueprint('logs', __name__)


@bp.route('/assets', methods=['GET'])
@jwt_required()
def get_asset_logs():
    """Récupérer les logs des assets"""
    db = get_db()

    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        asset_id = request.args.get('asset_id', type=int)
        user_id = request.args.get('user_id', type=int)
        action = request.args.get('action')

        query = db.query(Log)

        if asset_id:
            query = query.filter(Log.asset_id == asset_id)
        if user_id:
            query = query.filter(Log.user_id == user_id)
        if action:
            query = query.filter(Log.action == action)

        query = query.order_by(Log.D.desc())
        total = query.count()
        logs = query.offset((page - 1) * per_page).limit(per_page).all()

        logs_data = []
        for log in logs:
            user = db.query(User).filter_by(id=log.user_id).first()
            asset = db.query(Asset).filter_by(id=log.asset_id).first()

            logs_data.append({
                'id': log.id,
                'date': log.D.isoformat() if log.D else None,
                'action': log.action,
                'description': log.desc,
                'user': {'id': user.id, 'username': user.username} if user else None,
                'asset': {'id': asset.id, 'nom': asset.nom} if asset else None
            })

        return jsonify({
            'logs': logs_data,
            'pagination': {'page': page, 'per_page': per_page, 'total': total, 'pages': (total + per_page - 1) // per_page}
        }), 200

    finally:
        db.close()


@bp.route('/admin', methods=['GET'])
@jwt_required()
def get_admin_logs():
    """Récupérer les logs admin"""
    identity = get_jwt_identity()
    db = get_db()

    try:
        if identity['role'] not in ['ADMIN', 'MODERATOR']:
            return jsonify({'error': 'Permission refusée'}), 403

        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        user_id = request.args.get('user_id', type=int)

        query = db.query(LogAdmin)

        if user_id:
            query = query.filter(LogAdmin.user_id == user_id)

        query = query.order_by(LogAdmin.D.desc())
        total = query.count()
        logs = query.offset((page - 1) * per_page).limit(per_page).all()

        logs_data = [{
            'id': log.id,
            'date': log.D.isoformat() if log.D else None,
            'action': log.action,
            'description': log.desc,
            'admin_id': log.admin_id,
            'user_id': log.user_id
        } for log in logs]

        return jsonify({
            'logs': logs_data,
            'pagination': {'page': page, 'per_page': per_page, 'total': total, 'pages': (total + per_page - 1) // per_page}
        }), 200

    finally:
        db.close()


@bp.route('/missions/<int:mission_id>', methods=['GET'])
@jwt_required()
def get_mission_logs(mission_id):
    """Récupérer les logs d'une mission"""
    db = get_db()

    try:
        logs = db.query(LogMission).filter_by(mission_id=mission_id).order_by(LogMission.D.desc()).all()

        logs_data = [{
            'id': log.id,
            'date': log.D.isoformat() if log.D else None,
            'action': log.action,
            'description': log.desc,
            'user_id': log.user_id
        } for log in logs]

        return jsonify({'logs': logs_data}), 200

    finally:
        db.close()
