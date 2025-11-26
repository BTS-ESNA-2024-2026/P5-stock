"""
Blueprint Gestion des Équipements de Protection Personnelle (PP)
[EF-601-P à EF-604-I] Gestion des équipements de protection
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('pp', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_pp():
    """[EF-601-P] Récupérer la liste des équipements de protection"""
    # TODO: Implement with filters (size, certification, mandatory, etc.)
    return jsonify({'pp': []}), 200


@bp.route('/<int:pp_id>', methods=['GET'])
@jwt_required()
def get_pp_details(pp_id):
    """Récupérer les détails d'un équipement"""
    # TODO: Implement
    return jsonify({'pp': {}}), 200


@bp.route('/', methods=['POST'])
@jwt_required()
def create_pp():
    """
    [EF-601-P] Enregistrer un nouvel équipement de protection

    Body:
        pp_type_id, size, quantity, mandatory, certification_ids
    """
    # TODO: Implement with certifications (NIJ, STANAG, etc.)
    return jsonify({'message': 'Équipement créé'}), 201


@bp.route('/types', methods=['GET'])
@jwt_required()
def get_pp_types():
    """Récupérer les types d'équipements de protection"""
    # TODO: Query PPType table
    mock_types = [
        {
            'id': 1,
            'name': 'Gilet pare-balles',
            'description': 'Gilet de protection balistique',
            'category': 'Protection corporelle',
            'certification': 'NIJ Level IV'
        }
    ]
    return jsonify({'pp_types': mock_types}), 200


@bp.route('/mandatory', methods=['GET'])
@jwt_required()
def get_mandatory_pp():
    """[EF-603-I] Récupérer les équipements obligatoires"""
    # TODO: Query PP where mandatory=true
    return jsonify({'mandatory_pp': []}), 200
