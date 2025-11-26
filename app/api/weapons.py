"""
Blueprint Gestion des Armes
[EF-201-P à EF-207-I] Gestion des stocks d'armement
Cas d'utilisation UC-03
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

bp = Blueprint('weapons', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_weapons():
    """
    [EF-201-P] Récupérer la liste des armes
    Tous les utilisateurs peuvent lire

    Query params:
        page, per_page, search, status, type_id, location_id
    """
    identity = get_jwt_identity()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')
    type_id = request.args.get('type_id', type=int)

    # TODO: Query database with filters
    # weapons = Weapon.query.filter(...)

    mock_weapons = [
        {
            'id': 1,
            'sn': 'FAMAS-2025-001',
            'weapon_type_id': 1,
            'weapon_type': {
                'id': 1,
                'name': 'FAMAS F1',
                'type': 'Fusil d\'assaut',
                'calibre': '5.56x45mm NATO',
                'brand': 'Nexter'
            },
            'status': 'AVAILABLE',
            'last_revision': '2025-01-15',
            'next_revision': '2025-07-15',
            'entry_date': '2024-01-10',
            'location': {
                'building': 'Bâtiment A',
                'room': 'Armurerie',
                'section': 'Zone 1'
            }
        }
    ]

    return jsonify({
        'weapons': mock_weapons,
        'total': len(mock_weapons),
        'page': page,
        'per_page': per_page
    }), 200


@bp.route('/<int:weapon_id>', methods=['GET'])
@jwt_required()
def get_weapon(weapon_id):
    """Récupérer les détails d'une arme"""
    identity = get_jwt_identity()

    # TODO: Query database
    # weapon = Weapon.query.get_or_404(weapon_id)

    mock_weapon = {
        'id': weapon_id,
        'sn': 'FAMAS-2025-001',
        'status': 'AVAILABLE',
        'history': []  # LogMatos entries
    }

    return jsonify({'weapon': mock_weapon}), 200


@bp.route('/', methods=['POST'])
@jwt_required()
def create_weapon():
    """
    [EF-201-P] Enregistrer une nouvelle arme
    Rôle requis: ADMIN, LOGISTICIEN
    Cas d'utilisation UC-03

    Body:
        sn: str (unique)
        weapon_type_id: int
        entry_date: date
        location_id: int
        last_revision: date
        next_revision: date
    """
    identity = get_jwt_identity()

    # TODO: Vérifier le rôle
    # if identity.get('role') not in ['ADMIN', 'LOGISTICIEN']:
    #     return jsonify({'error': 'Permission refusée'}), 403

    data = request.get_json()

    required_fields = ['sn', 'weapon_type_id', 'entry_date', 'location_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Champ {field} requis'}), 400

    # TODO: Vérifier l'unicité du SN
    # existing = Weapon.query.filter_by(sn=data['sn']).first()
    # if existing:
    #     return jsonify({'error': 'SN déjà existant'}), 409

    # TODO: Créer l'arme dans la DB
    # new_weapon = Weapon(**data)
    # db.session.add(new_weapon)
    # db.session.commit()

    # TODO: Logger dans LogMatos
    current_app.logger.info(f'Arme créée: {data["sn"]} par {identity.get("username")}')

    return jsonify({
        'message': 'Arme enregistrée avec succès',
        'weapon': {'id': 999, 'sn': data['sn']}
    }), 201


@bp.route('/<int:weapon_id>', methods=['PUT'])
@jwt_required()
def update_weapon(weapon_id):
    """
    Modifier une arme
    Rôle requis: ADMIN, LOGISTICIEN
    """
    identity = get_jwt_identity()

    # TODO: Vérifier le rôle et update
    data = request.get_json()

    current_app.logger.info(f'Arme {weapon_id} modifiée par {identity.get("username")}')

    return jsonify({'message': 'Arme mise à jour avec succès'}), 200


@bp.route('/<int:weapon_id>/status', methods=['PATCH'])
@jwt_required()
def update_weapon_status(weapon_id):
    """
    [EF-203-P] Changer le statut d'une arme
    Status: AVAILABLE, IN_USE, MAINTENANCE, RETIRED, DAMAGED, LOST

    Body:
        status: str
        notes: str (optional)
    """
    identity = get_jwt_identity()
    data = request.get_json()

    valid_statuses = ['AVAILABLE', 'IN_USE', 'MAINTENANCE', 'RETIRED', 'DAMAGED', 'LOST']
    if data.get('status') not in valid_statuses:
        return jsonify({'error': f'Statut invalide. Valeurs: {valid_statuses}'}), 400

    # TODO: Update status and log in LogMatos

    current_app.logger.info(f'Statut arme {weapon_id} changé en {data["status"]}')

    return jsonify({'message': 'Statut mis à jour avec succès'}), 200


@bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_weapon_alerts():
    """
    [EF-205-I] Récupérer les alertes de révision
    Alertes pour les armes dont nextRevision < 30 jours
    """
    identity = get_jwt_identity()

    # TODO: Query weapons with upcoming revisions
    # threshold_date = datetime.utcnow() + timedelta(days=30)
    # weapons = Weapon.query.filter(Weapon.next_revision <= threshold_date)

    mock_alerts = [
        {
            'id': 1,
            'sn': 'FAMAS-2025-001',
            'next_revision': (datetime.now() + timedelta(days=15)).isoformat(),
            'days_remaining': 15,
            'priority': 'medium'
        }
    ]

    return jsonify({'alerts': mock_alerts}), 200


@bp.route('/types', methods=['GET'])
@jwt_required()
def get_weapon_types():
    """Récupérer la liste des types d'armes (WeaponType)"""
    # TODO: Query WeaponType table

    mock_types = [
        {
            'id': 1,
            'name': 'FAMAS F1',
            'description': 'Fusil d\'assaut français',
            'type': 'Fusil d\'assaut',
            'calibre': '5.56x45mm NATO',
            'brand': 'Nexter'
        }
    ]

    return jsonify({'weapon_types': mock_types}), 200


@bp.route('/types', methods=['POST'])
@jwt_required()
def create_weapon_type():
    """
    Créer un nouveau type d'arme
    Rôle requis: ADMIN

    Body:
        name, description, type, calibre, brand
    """
    identity = get_jwt_identity()
    data = request.get_json()

    # TODO: Create weapon type

    return jsonify({'message': 'Type d\'arme créé avec succès'}), 201
