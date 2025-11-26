"""
Middleware d'authentification et de logging
[ES-501-P] Logging de toutes les actions
"""

from flask import request, current_app, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from datetime import datetime
import json


def log_request_middleware():
    """
    [ES-501-P] Enregistre toutes les requêtes pour l'audit
    Exécuté avant chaque requête

    Log les informations:
        - Timestamp
        - Méthode HTTP
        - URL
        - User ID (si authentifié)
        - IP address
        - User agent
    """
    # Ignorer les routes de santé et statiques
    if request.path in ['/health', '/favicon.ico']:
        return

    # Essayer de récupérer l'utilisateur authentifié
    user_id = None
    username = None

    try:
        # Vérifier JWT sans lever d'exception
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            user_id = identity.get('user_id')
            username = identity.get('username')
    except Exception:
        # Pas d'authentification, c'est OK
        pass

    # Stocker dans g pour accès dans les routes
    g.user_id = user_id
    g.username = username
    g.ip_address = request.remote_addr
    g.request_timestamp = datetime.utcnow()

    # Logger la requête (seulement en mode verbose)
    if current_app.debug:
        current_app.logger.debug(
            f'{request.method} {request.path} - '
            f'User: {username or "anonymous"} - '
            f'IP: {request.remote_addr}'
        )


def log_response_middleware(response):
    """
    Exécuté après chaque requête
    Log les erreurs et actions sensibles
    """
    # Logger les erreurs
    if response.status_code >= 400:
        current_app.logger.warning(
            f'Error {response.status_code} - '
            f'{request.method} {request.path} - '
            f'User: {getattr(g, "username", "anonymous")} - '
            f'IP: {request.remote_addr}'
        )

    # TODO: Pour les actions sensibles (POST, PUT, DELETE), logger dans la DB
    # if request.method in ['POST', 'PUT', 'DELETE'] and response.status_code < 400:
    #     log_entry = LogAdmin(
    #         user_id=getattr(g, 'user_id', None),
    #         action=f'{request.method} {request.path}',
    #         description=f'Request to {request.path}',
    #         date=getattr(g, 'request_timestamp', datetime.utcnow()),
    #         ip_address=request.remote_addr
    #     )
    #     db.session.add(log_entry)
    #     db.session.commit()

    return response


def check_jwt_blacklist(jwt_header, jwt_payload):
    """
    [ES-106-P] Vérifier si le token est dans la blacklist
    Utilisé après logout ou révocation de token

    TODO: Implémenter avec Redis
    """
    jti = jwt_payload['jti']

    # TODO: Vérifier dans Redis
    # is_blacklisted = redis_client.exists(f'blacklist:{jti}')
    # if is_blacklisted:
    #     raise Exception('Token has been revoked')

    return False


def track_failed_login(username, ip_address):
    """
    [ES-104-P] Suivre les tentatives de connexion échouées
    Bloquer après 5 tentatives

    TODO: Implémenter avec Redis pour le tracking
    """
    key = f'failed_login:{ip_address}:{username}'

    # TODO: Incrémenter dans Redis avec expiration
    # attempts = redis_client.incr(key)
    # redis_client.expire(key, 900)  # 15 minutes
    #
    # if attempts >= 5:
    #     # Bloquer l'IP/utilisateur
    #     redis_client.setex(f'blocked:{ip_address}:{username}', 900, 'true')
    #     return True
    #
    # return False

    return False


def is_blocked(username, ip_address):
    """
    [ES-104-P] Vérifier si un utilisateur/IP est bloqué

    TODO: Implémenter avec Redis
    """
    key = f'blocked:{ip_address}:{username}'

    # TODO: Vérifier dans Redis
    # return redis_client.exists(key)

    return False


def clear_failed_login(username, ip_address):
    """
    Réinitialiser le compteur de tentatives échouées après succès
    """
    key = f'failed_login:{ip_address}:{username}'

    # TODO: Supprimer de Redis
    # redis_client.delete(key)

    pass
