"""
Blueprint Authentification
Gestion de l'authentification avec JWT et MFA (TOTP)
Conformité ANSSI: ES-101 à ES-108
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from datetime import datetime
import pyotp
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.models.models import User, Group, LogAdmin
from app.utils.password import hash_password, verify_password
from app.utils.validators import validate_password, validate_username
from app.utils.decorators import validate_request

bp = Blueprint('auth', __name__)


# Compteur de tentatives de connexion échouées (à stocker en Redis en production)
login_attempts = {}


@bp.route('/login', methods=['POST'])
def login():
    """
    [EF-101-P] Authentification utilisateur
    Cas d'utilisation UC-01

    Body:
        username: str
        password: str

    Returns:
        - Sans MFA: access_token et refresh_token
        - Avec MFA: mfa_required=True et temp_token
    """
    data = request.get_json(silent=True, force=True)

    if not data:
        current_app.logger.error(f'No JSON data received. Content-Type: {request.content_type}')
        return jsonify({'error': 'Aucune donnée JSON reçue'}), 400

    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Identifiants manquants'}), 400

    username = data.get('username')
    password = data.get('password')

    db = get_db()

    try:
        # Récupérer l'utilisateur
        user = db.query(User).filter_by(username=username).first()

        if not user:
            current_app.logger.warning(f'Tentative de connexion échouée: utilisateur inconnu {username}')
            return jsonify({'error': 'Identifiants invalides'}), 401

        # Vérifier si le compte est actif
        if not user.active:
            current_app.logger.warning(f'Tentative de connexion sur compte inactif: {username}')
            return jsonify({'error': 'Compte désactivé'}), 403

        # Vérifier la période de validité du compte
        now = datetime.utcnow()
        if now < user.DA or now > user.DE:
            current_app.logger.warning(f'Compte hors période de validité: {username}')
            return jsonify({'error': 'Compte expiré ou pas encore actif'}), 403

        # [ES-104-P] Vérifier les tentatives de connexion (anti-brute force)
        ip_address = request.remote_addr
        attempts_key = f'{username}:{ip_address}'

        if attempts_key in login_attempts and login_attempts[attempts_key] >= 5:
            current_app.logger.warning(f'Compte bloqué (trop de tentatives): {username} depuis {ip_address}')
            return jsonify({'error': 'Compte temporairement bloqué. Réessayez dans 15 minutes.'}), 429

        # Vérifier le mot de passe
        if not verify_password(password, user.hash):
            # Incrémenter le compteur de tentatives
            login_attempts[attempts_key] = login_attempts.get(attempts_key, 0) + 1

            current_app.logger.warning(
                f'Mot de passe invalide pour {username} (tentative {login_attempts[attempts_key]})'
            )

            return jsonify({'error': 'Identifiants invalides'}), 401

        # Réinitialiser le compteur de tentatives en cas de succès
        if attempts_key in login_attempts:
            del login_attempts[attempts_key]

        # Récupérer le groupe et le rôle
        group = db.query(Group).filter_by(id=user.group_id).first()

        if not group:
            current_app.logger.error(f'Groupe introuvable pour user {username}')
            return jsonify({'error': 'Configuration utilisateur invalide'}), 500

        # [ES-103-P] Vérifier si MFA est activé
        if user.MFA:
            # Créer un token temporaire pour la validation MFA
            temp_token = create_access_token(
                identity={
                    'user_id': user.id,
                    'username': user.username,
                    'mfa_validated': False
                }
            )
            return jsonify({
                'mfa_required': True,
                'temp_token': temp_token,
                'message': 'Veuillez entrer votre code MFA'
            }), 200

        # Sans MFA, créer les tokens directement
        access_token = create_access_token(
            identity={
                'user_id': user.id,
                'username': user.username,
                'role': group.name,
                'group_id': user.group_id
            }
        )
        refresh_token = create_refresh_token(
            identity={'user_id': user.id}
        )

        # [ES-501-P] Enregistrer la connexion dans LogAdmin
        log_entry = LogAdmin(
            admin_id=user.id,
            user_id=user.id,
            D=datetime.utcnow(),
            action='LOGIN',
            desc=f'Connexion réussie depuis {ip_address}'
        )
        db.add(log_entry)
        db.commit()

        current_app.logger.info(f'Connexion réussie: {username}')

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'role': group.name
            }
        }), 200

    except SQLAlchemyError as e:
        db.rollback()
        current_app.logger.error(f'Erreur DB lors du login: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/verify-mfa', methods=['POST'])
@jwt_required()
@validate_request('code')
def verify_mfa():
    """
    [ES-103-P] Vérification du code MFA (TOTP)
    Cas d'utilisation UC-01 (étape MFA)

    Body:
        code: str (6 digits)

    Returns:
        access_token et refresh_token définitifs
    """
    data = request.get_json()
    code = data.get('code')

    if len(code) != 6:
        return jsonify({'error': 'Code MFA invalide'}), 400

    # Récupérer l'identité du token temporaire
    identity = get_jwt_identity()

    if identity.get('mfa_validated'):
        return jsonify({'error': 'MFA déjà validé'}), 400

    user_id = identity.get('user_id')
    db = get_db()

    try:
        # Récupérer l'utilisateur et son secret MFA
        user = db.query(User).filter_by(id=user_id).first()

        if not user or not user.MFA:
            return jsonify({'error': 'MFA non configuré'}), 400

        # Vérifier le code TOTP
        totp = pyotp.TOTP(user.MFA)
        is_valid = totp.verify(code, valid_window=1)  # Fenêtre de 30s avant/après

        if not is_valid:
            current_app.logger.warning(f'Code MFA invalide pour user_id {user_id}')
            return jsonify({'error': 'Code MFA incorrect'}), 401

        # Récupérer le groupe
        group = db.query(Group).filter_by(id=user.group_id).first()

        # Créer les tokens définitifs
        access_token = create_access_token(
            identity={
                'user_id': user.id,
                'username': user.username,
                'role': group.name,
                'group_id': user.group_id,
                'mfa_validated': True
            }
        )
        refresh_token = create_refresh_token(
            identity={'user_id': user.id}
        )

        # Enregistrer dans les logs
        log_entry = LogAdmin(
            admin_id=user.id,
            user_id=user.id,
            D=datetime.utcnow(),
            action='MFA_VALIDATED',
            desc='Code MFA validé avec succès'
        )
        db.add(log_entry)
        db.commit()

        current_app.logger.info(f'MFA validé pour user_id {user_id}')

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'role': group.name
            }
        }), 200

    except SQLAlchemyError as e:
        db.rollback()
        current_app.logger.error(f'Erreur DB lors de la vérification MFA: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Rafraîchir le token d'accès

    Returns:
        Nouveau access_token
    """
    identity = get_jwt_identity()
    db = get_db()

    try:
        # Vérifier que l'utilisateur existe toujours et est actif
        user = db.query(User).filter_by(id=identity['user_id']).first()

        if not user or not user.active:
            return jsonify({'error': 'Utilisateur inactif ou introuvable'}), 401

        # Récupérer le groupe
        group = db.query(Group).filter_by(id=user.group_id).first()

        new_access_token = create_access_token(
            identity={
                'user_id': user.id,
                'username': user.username,
                'role': group.name,
                'group_id': user.group_id
            }
        )

        return jsonify({'access_token': new_access_token}), 200

    except SQLAlchemyError as e:
        current_app.logger.error(f'Erreur DB lors du refresh: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Déconnexion utilisateur
    TODO: Ajouter le token à une blacklist Redis
    """
    identity = get_jwt_identity()
    jti = get_jwt()['jti']  # JWT ID pour blacklist
    db = get_db()

    try:
        # Enregistrer la déconnexion
        log_entry = LogAdmin(
            admin_id=identity['user_id'],
            user_id=identity['user_id'],
            D=datetime.utcnow(),
            action='LOGOUT',
            desc='Déconnexion utilisateur'
        )
        db.add(log_entry)
        db.commit()

        # TODO: Ajouter le jti à la blacklist Redis
        # redis_client.setex(f'blacklist:{jti}', JWT_ACCESS_TOKEN_EXPIRES, 'true')

        current_app.logger.info(f'Déconnexion user_id {identity.get("user_id")}')

        return jsonify({'message': 'Déconnexion réussie'}), 200

    except SQLAlchemyError as e:
        db.rollback()
        current_app.logger.error(f'Erreur DB lors du logout: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/setup-mfa', methods=['POST'])
@jwt_required()
def setup_mfa():
    """
    [ES-103-P] Configuration du MFA pour un utilisateur
    Génère un nouveau secret TOTP et retourne l'URI du QR code

    Returns:
        secret: str (à stocker côté serveur)
        qr_code_uri: str (pour générer le QR code côté client)
    """
    identity = get_jwt_identity()
    user_id = identity.get('user_id')
    db = get_db()

    try:
        user = db.query(User).filter_by(id=user_id).first()

        if not user:
            return jsonify({'error': 'Utilisateur introuvable'}), 404

        # Générer un nouveau secret TOTP
        secret = pyotp.random_base32()

        # Créer l'URI pour le QR code
        totp = pyotp.TOTP(secret)
        issuer_name = current_app.config['MFA_ISSUER_NAME']
        qr_code_uri = totp.provisioning_uri(
            name=user.username,
            issuer_name=issuer_name
        )

        # Stocker le secret temporairement (pas encore activé)
        # On ne l'active qu'après confirmation avec confirm-mfa
        user.MFA = secret
        db.commit()

        current_app.logger.info(f'Configuration MFA initiée pour user_id {user_id}')

        return jsonify({
            'secret': secret,
            'qr_code_uri': qr_code_uri,
            'message': 'Scannez le QR code avec votre application d\'authentification et confirmez avec un code'
        }), 200

    except SQLAlchemyError as e:
        db.rollback()
        current_app.logger.error(f'Erreur DB lors de la configuration MFA: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/confirm-mfa', methods=['POST'])
@jwt_required()
@validate_request('code')
def confirm_mfa():
    """
    Confirmer l'activation du MFA en validant un premier code

    Body:
        code: str (6 digits)

    Returns:
        Confirmation de l'activation du MFA
    """
    data = request.get_json()
    code = data.get('code')

    if len(code) != 6:
        return jsonify({'error': 'Code MFA invalide'}), 400

    identity = get_jwt_identity()
    user_id = identity.get('user_id')
    db = get_db()

    try:
        user = db.query(User).filter_by(id=user_id).first()

        if not user or not user.MFA:
            return jsonify({'error': 'MFA non configuré'}), 400

        # Vérifier le code TOTP
        totp = pyotp.TOTP(user.MFA)
        is_valid = totp.verify(code, valid_window=1)

        if not is_valid:
            return jsonify({'error': 'Code MFA incorrect'}), 401

        # MFA confirmé et activé
        log_entry = LogAdmin(
            admin_id=user_id,
            user_id=user_id,
            D=datetime.utcnow(),
            action='MFA_ENABLED',
            desc='MFA activé avec succès'
        )
        db.add(log_entry)
        db.commit()

        current_app.logger.info(f'MFA activé pour user_id {user_id}')

        return jsonify({'message': 'MFA activé avec succès'}), 200

    except SQLAlchemyError as e:
        db.rollback()
        current_app.logger.error(f'Erreur DB lors de la confirmation MFA: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/disable-mfa', methods=['POST'])
@jwt_required()
@validate_request('code')
def disable_mfa():
    """
    Désactiver le MFA (nécessite confirmation par code)

    Body:
        code: str (6 digits)

    Returns:
        Confirmation de la désactivation du MFA
    """
    data = request.get_json()
    code = data.get('code')

    if len(code) != 6:
        return jsonify({'error': 'Code MFA invalide'}), 400

    identity = get_jwt_identity()
    user_id = identity.get('user_id')
    db = get_db()

    try:
        user = db.query(User).filter_by(id=user_id).first()

        if not user or not user.MFA:
            return jsonify({'error': 'MFA non configuré'}), 400

        # Vérifier le code TOTP avant de désactiver
        totp = pyotp.TOTP(user.MFA)
        is_valid = totp.verify(code, valid_window=1)

        if not is_valid:
            return jsonify({'error': 'Code MFA incorrect'}), 401

        # Désactiver le MFA
        user.MFA = None
        log_entry = LogAdmin(
            admin_id=user_id,
            user_id=user_id,
            D=datetime.utcnow(),
            action='MFA_DISABLED',
            desc='MFA désactivé'
        )
        db.add(log_entry)
        db.commit()

        current_app.logger.info(f'MFA désactivé pour user_id {user_id}')

        return jsonify({'message': 'MFA désactivé avec succès'}), 200

    except SQLAlchemyError as e:
        db.rollback()
        current_app.logger.error(f'Erreur DB lors de la désactivation MFA: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Récupérer les informations de l'utilisateur connecté

    Returns:
        Informations de l'utilisateur
    """
    identity = get_jwt_identity()
    db = get_db()

    try:
        user = db.query(User).filter_by(id=identity['user_id']).first()

        if not user:
            return jsonify({'error': 'Utilisateur introuvable'}), 404

        group = db.query(Group).filter_by(id=user.group_id).first()

        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'role': group.name if group else None,
                'group_id': user.group_id,
                'active': user.active,
                'mfa_enabled': user.MFA is not None,
                'valid_from': user.DA.isoformat(),
                'valid_until': user.DE.isoformat()
            }
        }), 200

    except SQLAlchemyError as e:
        current_app.logger.error(f'Erreur DB lors de la récupération de l\'utilisateur: {str(e)}')
        return jsonify({'error': 'Erreur interne du serveur'}), 500

    finally:
        db.close()
