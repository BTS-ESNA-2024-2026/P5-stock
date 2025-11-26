"""
Blueprint Gestion des Utilisateurs
CRUD utilisateurs avec contrôle d'accès RBAC
Conformité: EF-101 à EF-107, UC-02
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.database import get_db
from app.models.models import User, Group, LogAdmin
from app.utils.password import hash_password, generate_secure_password
from app.utils.validators import validate_password, validate_username
from app.utils.decorators import admin_required, validate_request

bp = Blueprint('users', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def list_users():
    """
    [EF-101-P] Lister tous les utilisateurs

    Query params:
        page: int (default 1)
        per_page: int (default 20, max 100)
        active: bool (filter par statut actif)
        group_id: int (filter par groupe)
        search: str (recherche par username ou name)

    Returns:
        Liste paginée des utilisateurs
    """
    identity = get_jwt_identity()
    db = get_db()

    try:
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)

        # Filtres
        active = request.args.get('active', type=lambda v: v.lower() == 'true')
        group_id = request.args.get('group_id', type=int)
        search = request.args.get('search', type=str)

        # Query de base
        query = db.query(User)

        # Appliquer les filtres
        if active is not None:
            query = query.filter(User.active == active)
        if group_id:
            query = query.filter(User.group_id == group_id)
        if search:
            query = query.filter(
                (User.username.like(f'%{search}%')) |
                (User.name.like(f'%{search}%'))
            )

        # Compter le total
        total = query.count()

        # Paginer
        offset = (page - 1) * per_page
        users = query.offset(offset).limit(per_page).all()

        # Formater la réponse
        users_data = []
        for user in users:
            group = db.query(Group).filter_by(id=user.group_id).first()
            users_data.append({
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'group': {
                    'id': group.id,
                    'name': group.name
                } if group else None,
                'active': user.active,
                'mfa_enabled': user.MFA is not None,
                'valid_from': user.DA.isoformat(),
                'valid_until': user.DE.isoformat()
            })

        return jsonify({
            'users': users_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200

    except SQLAlchemyError as e:
        current_app.logger.error(f'Erreur DB lors de la liste des utilisateurs: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Récupérer les détails d'un utilisateur

    Returns:
        Détails complets de l'utilisateur
    """
    identity = get_jwt_identity()
    db = get_db()

    try:
        user = db.query(User).filter_by(id=user_id).first()

        if not user:
            return jsonify({'error': 'Utilisateur introuvable'}), 404

        # Vérifier les permissions (un utilisateur ne peut voir que lui-même sauf admin)
        if identity['role'] != 'ADMIN' and identity['user_id'] != user_id:
            return jsonify({'error': 'Accès interdit'}), 403

        group = db.query(Group).filter_by(id=user.group_id).first()

        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'group': {
                    'id': group.id,
                    'name': group.name,
                    'description': group.desc,
                    'permissions': group.perms
                } if group else None,
                'active': user.active,
                'mfa_enabled': user.MFA is not None,
                'hash_algorithm': user.hash_algorithm,
                'valid_from': user.DA.isoformat(),
                'valid_until': user.DE.isoformat()
            }
        }), 200

    except SQLAlchemyError as e:
        current_app.logger.error(f'Erreur DB lors de la récupération utilisateur: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('', methods=['POST'])
@jwt_required()
@admin_required
@validate_request('username', 'name', 'group_id')
def create_user():
    """
    [EF-101-P] Créer un nouvel utilisateur (Admin seulement)
    Cas d'utilisation UC-02

    Body:
        username: str (required)
        name: str (required)
        group_id: int (required)
        password: str (optional, auto-généré si absent)
        valid_from: str ISO date (optional, default now)
        valid_until: str ISO date (optional, default +1 year)
        active: bool (optional, default True)

    Returns:
        Utilisateur créé avec mot de passe temporaire
    """
    identity = get_jwt_identity()
    data = request.get_json()

    username = data.get('username')
    name = data.get('name')
    group_id = data.get('group_id')
    password = data.get('password')
    valid_from = data.get('valid_from')
    valid_until = data.get('valid_until')
    active = data.get('active', True)

    db = get_db()

    try:
        # Valider le username
        is_valid, message = validate_username(username)
        if not is_valid:
            return jsonify({'error': message}), 400

        # Vérifier que le username n'existe pas déjà
        existing_user = db.query(User).filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': 'Ce nom d\'utilisateur existe déjà'}), 409

        # Vérifier que le groupe existe
        group = db.query(Group).filter_by(id=group_id).first()
        if not group:
            return jsonify({'error': 'Groupe introuvable'}), 404

        # Générer un mot de passe si non fourni
        if not password:
            password = generate_secure_password(16)
            password_auto_generated = True
        else:
            # Valider le mot de passe fourni
            is_valid, message = validate_password(password)
            if not is_valid:
                return jsonify({'error': message}), 400
            password_auto_generated = False

        # Hacher le mot de passe
        hash_str, algorithm = hash_password(password)

        # Dates de validité
        now = datetime.utcnow()
        DA = datetime.fromisoformat(valid_from) if valid_from else now
        DE = datetime.fromisoformat(valid_until) if valid_until else now + timedelta(days=365)

        # Créer l'utilisateur
        new_user = User(
            username=username,
            name=name,
            group_id=group_id,
            hash=hash_str,
            hash_algorithm=algorithm,
            active=active,
            DA=DA,
            DE=DE,
            MFA=None  # MFA désactivé par défaut
        )

        db.add(new_user)
        db.flush()  # Pour obtenir l'ID

        # Enregistrer dans les logs
        log_entry = LogAdmin(
            admin_id=identity['user_id'],
            user_id=new_user.id,
            D=datetime.utcnow(),
            action='USER_CREATED',
            desc=f'Utilisateur {username} créé par {identity["username"]}'
        )
        db.add(log_entry)
        db.commit()

        current_app.logger.info(f'Utilisateur créé: {username} (ID: {new_user.id})')

        response_data = {
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'name': new_user.name,
                'group': {
                    'id': group.id,
                    'name': group.name
                },
                'active': new_user.active,
                'valid_from': new_user.DA.isoformat(),
                'valid_until': new_user.DE.isoformat()
            }
        }

        # Retourner le mot de passe seulement s'il a été auto-généré
        if password_auto_generated:
            response_data['temporary_password'] = password
            response_data['message'] = 'Utilisateur créé avec succès. Mot de passe temporaire généré.'
        else:
            response_data['message'] = 'Utilisateur créé avec succès.'

        return jsonify(response_data), 201

    except IntegrityError as e:
        db.rollback()
        current_app.logger.error(f'Erreur d\'intégrité lors de la création utilisateur: {str(e)}')
        return jsonify({'error': 'Ce nom d\'utilisateur existe déjà'}), 409

    except SQLAlchemyError as e:
        db.rollback()
        current_app.logger.error(f'Erreur DB lors de la création utilisateur: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """
    Modifier un utilisateur
    Un utilisateur peut se modifier lui-même, un admin peut modifier n'importe qui

    Body:
        name: str (optional)
        group_id: int (optional, admin only)
        password: str (optional)
        valid_from: str ISO date (optional, admin only)
        valid_until: str ISO date (optional, admin only)

    Returns:
        Utilisateur modifié
    """
    identity = get_jwt_identity()
    data = request.get_json()
    db = get_db()

    try:
        user = db.query(User).filter_by(id=user_id).first()

        if not user:
            return jsonify({'error': 'Utilisateur introuvable'}), 404

        # Vérifier les permissions
        is_admin = identity['role'] == 'ADMIN'
        is_self = identity['user_id'] == user_id

        if not is_admin and not is_self:
            return jsonify({'error': 'Accès interdit'}), 403

        # Champs modifiables
        if 'name' in data:
            user.name = data['name']

        # Champs réservés aux admins
        if is_admin:
            if 'group_id' in data:
                group = db.query(Group).filter_by(id=data['group_id']).first()
                if not group:
                    return jsonify({'error': 'Groupe introuvable'}), 404
                user.group_id = data['group_id']

            if 'valid_from' in data:
                user.DA = datetime.fromisoformat(data['valid_from'])

            if 'valid_until' in data:
                user.DE = datetime.fromisoformat(data['valid_until'])

        # Changement de mot de passe (disponible pour soi-même ou admin)
        if 'password' in data and data['password']:
            # Valider le nouveau mot de passe
            is_valid, message = validate_password(data['password'])
            if not is_valid:
                return jsonify({'error': message}), 400

            # Hacher le nouveau mot de passe
            hash_str, algorithm = hash_password(data['password'])
            user.hash = hash_str
            user.hash_algorithm = algorithm

        # Enregistrer les modifications
        log_entry = LogAdmin(
            admin_id=identity['user_id'],
            user_id=user_id,
            D=datetime.utcnow(),
            action='USER_UPDATED',
            desc=f'Utilisateur {user.username} modifié par {identity["username"]}'
        )
        db.add(log_entry)
        db.commit()

        current_app.logger.info(f'Utilisateur modifié: {user.username} (ID: {user_id})')

        group = db.query(Group).filter_by(id=user.group_id).first()

        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'group': {
                    'id': group.id,
                    'name': group.name
                } if group else None,
                'active': user.active,
                'mfa_enabled': user.MFA is not None,
                'valid_from': user.DA.isoformat(),
                'valid_until': user.DE.isoformat()
            },
            'message': 'Utilisateur modifié avec succès'
        }), 200

    except SQLAlchemyError as e:
        db.rollback()
        current_app.logger.error(f'Erreur DB lors de la modification utilisateur: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """
    Supprimer (désactiver) un utilisateur (Admin seulement)
    Note: On ne supprime pas réellement l'utilisateur pour conserver l'historique

    Returns:
        Confirmation de désactivation
    """
    identity = get_jwt_identity()
    db = get_db()

    try:
        user = db.query(User).filter_by(id=user_id).first()

        if not user:
            return jsonify({'error': 'Utilisateur introuvable'}), 404

        # Empêcher la suppression de soi-même
        if user_id == identity['user_id']:
            return jsonify({'error': 'Vous ne pouvez pas supprimer votre propre compte'}), 400

        # Désactiver l'utilisateur au lieu de le supprimer
        user.active = False

        # Enregistrer dans les logs
        log_entry = LogAdmin(
            admin_id=identity['user_id'],
            user_id=user_id,
            D=datetime.utcnow(),
            action='USER_DELETED',
            desc=f'Utilisateur {user.username} désactivé par {identity["username"]}'
        )
        db.add(log_entry)
        db.commit()

        current_app.logger.info(f'Utilisateur désactivé: {user.username} (ID: {user_id})')

        return jsonify({'message': 'Utilisateur désactivé avec succès'}), 200

    except SQLAlchemyError as e:
        db.rollback()
        current_app.logger.error(f'Erreur DB lors de la suppression utilisateur: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/<int:user_id>/activate', methods=['PATCH'])
@jwt_required()
@admin_required
def activate_user(user_id):
    """
    Activer un utilisateur désactivé (Admin seulement)

    Returns:
        Confirmation d'activation
    """
    identity = get_jwt_identity()
    db = get_db()

    try:
        user = db.query(User).filter_by(id=user_id).first()

        if not user:
            return jsonify({'error': 'Utilisateur introuvable'}), 404

        user.active = True

        log_entry = LogAdmin(
            admin_id=identity['user_id'],
            user_id=user_id,
            D=datetime.utcnow(),
            action='USER_ACTIVATED',
            desc=f'Utilisateur {user.username} activé par {identity["username"]}'
        )
        db.add(log_entry)
        db.commit()

        current_app.logger.info(f'Utilisateur activé: {user.username} (ID: {user_id})')

        return jsonify({'message': 'Utilisateur activé avec succès'}), 200

    except SQLAlchemyError as e:
        db.rollback()
        current_app.logger.error(f'Erreur DB lors de l\'activation utilisateur: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/groups', methods=['GET'])
@jwt_required()
def list_groups():
    """
    Lister tous les groupes disponibles

    Returns:
        Liste des groupes
    """
    db = get_db()

    try:
        groups = db.query(Group).all()

        groups_data = [{
            'id': group.id,
            'name': group.name,
            'description': group.desc,
            'permissions': group.perms
        } for group in groups]

        return jsonify({'groups': groups_data}), 200

    except SQLAlchemyError as e:
        current_app.logger.error(f'Erreur DB lors de la liste des groupes: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()
