"""
Décorateurs personnalisés
Gestion des rôles et permissions (RBAC)
[ES-201-P à ES-204-I] Contrôle d'accès
"""

from functools import wraps
from flask import jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity


def role_required(*allowed_roles):
    """
    [ES-201-P] Décorateur pour vérifier le rôle de l'utilisateur

    Usage:
        @role_required('ADMIN')
        def admin_only_route():
            ...

        @role_required('ADMIN', 'MODERATOR')
        def admin_or_moderator_route():
            ...

    Args:
        allowed_roles: tuple de str - Rôles autorisés

    Returns:
        Décorateur de fonction
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()

            user_role = identity.get('role')

            if user_role not in allowed_roles:
                current_app.logger.warning(
                    f'Accès refusé: User {identity.get("username")} (role: {user_role}) '
                    f'attempted to access route requiring roles: {allowed_roles}'
                )
                return jsonify({
                    'error': 'forbidden',
                    'message': 'Accès interdit. Permissions insuffisantes.'
                }), 403

            return fn(*args, **kwargs)

        return wrapper
    return decorator


def admin_required(fn):
    """
    [ES-201-P] Décorateur pour routes réservées aux administrateurs

    Usage:
        @admin_required
        def admin_route():
            ...
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()

        if identity.get('role') != 'ADMIN':
            current_app.logger.warning(
                f'Accès administrateur refusé: User {identity.get("username")}'
            )
            return jsonify({
                'error': 'forbidden',
                'message': 'Accès réservé aux administrateurs'
            }), 403

        return wrapper(*args, **kwargs)

    return wrapper


def permission_required(*permissions):
    """
    [ES-203-P] Décorateur pour vérifier des permissions spécifiques

    Permissions:
        - read:users, write:users, delete:users
        - read:weapons, write:weapons, delete:weapons
        - read:vehicles, write:vehicles, delete:vehicles
        - read:missions, write:missions, delete:missions
        - read:logs, export:logs
        - read:reports, export:reports

    Usage:
        @permission_required('write:weapons', 'write:vehicles')
        def create_material():
            ...

    Args:
        permissions: tuple de str - Permissions requises

    Returns:
        Décorateur de fonction
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()

            # TODO: Récupérer les permissions depuis la DB via le groupe (GP)
            # user_permissions = get_user_permissions(identity.get('user_id'))

            # Mock pour le moment - les admins ont toutes les permissions
            if identity.get('role') == 'ADMIN':
                return fn(*args, **kwargs)

            # TODO: Vérifier les permissions
            # for perm in permissions:
            #     if perm not in user_permissions:
            #         current_app.logger.warning(
            #             f'Permission refusée: User {identity.get("username")} '
            #             f'missing permission: {perm}'
            #         )
            #         return jsonify({
            #             'error': 'forbidden',
            #             'message': f'Permission manquante: {perm}'
            #         }), 403

            return fn(*args, **kwargs)

        return wrapper
    return decorator


def log_action(action_type, entity_type=None):
    """
    [ES-501-P] Décorateur pour logger automatiquement les actions

    Usage:
        @log_action('CREATE', 'weapon')
        def create_weapon():
            ...

    Args:
        action_type: str - Type d'action (CREATE, UPDATE, DELETE, READ)
        entity_type: str - Type d'entité concernée (weapon, vehicle, etc.)

    Returns:
        Décorateur de fonction
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()

            # Exécuter la fonction
            result = fn(*args, **kwargs)

            # Logger l'action
            # TODO: Ajouter dans LogMatos ou LogAdmin selon entity_type
            current_app.logger.info(
                f'Action logged: {action_type} {entity_type or "resource"} '
                f'by user {identity.get("username")}'
            )

            # TODO: Insérer dans la DB
            # if entity_type:
            #     log_entry = LogMatos(
            #         user_id=identity.get('user_id'),
            #         action=action_type,
            #         description=f'{action_type} {entity_type}',
            #         date=datetime.utcnow()
            #     )
            # else:
            #     log_entry = LogAdmin(...)
            # db.session.add(log_entry)
            # db.session.commit()

            return result

        return wrapper
    return decorator


def rate_limit(max_requests=10, window=60):
    """
    [ES-404-P] Décorateur pour limiter le nombre de requêtes

    Usage:
        @rate_limit(max_requests=5, window=60)  # 5 requêtes par minute
        def sensitive_route():
            ...

    Args:
        max_requests: int - Nombre max de requêtes
        window: int - Fenêtre de temps en secondes

    Returns:
        Décorateur de fonction
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from flask import request

            # TODO: Implémenter avec Redis
            # key = f'rate_limit:{request.remote_addr}:{fn.__name__}'
            # requests = redis_client.incr(key)
            # if requests == 1:
            #     redis_client.expire(key, window)
            #
            # if requests > max_requests:
            #     current_app.logger.warning(
            #         f'Rate limit exceeded: {request.remote_addr} on {fn.__name__}'
            #     )
            #     return jsonify({
            #         'error': 'rate_limit_exceeded',
            #         'message': 'Trop de requêtes. Réessayez plus tard.'
            #     }), 429

            return fn(*args, **kwargs)

        return wrapper
    return decorator


def validate_request(*fields):
    """
    Décorateur pour valider les champs requis dans la requête

    Usage:
        @validate_request('username', 'password', 'email')
        def create_user():
            ...

    Args:
        fields: tuple de str - Champs requis

    Returns:
        Décorateur de fonction
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from flask import request

            data = request.get_json()

            if not data:
                return jsonify({
                    'error': 'bad_request',
                    'message': 'Body JSON requis'
                }), 400

            missing_fields = []
            for field in fields:
                if field not in data or not data[field]:
                    missing_fields.append(field)

            if missing_fields:
                return jsonify({
                    'error': 'bad_request',
                    'message': f'Champs manquants: {", ".join(missing_fields)}'
                }), 400

            return fn(*args, **kwargs)

        return wrapper
    return decorator


def cache_response(timeout=300):
    """
    Décorateur pour mettre en cache les réponses

    Usage:
        @cache_response(timeout=600)  # Cache pendant 10 minutes
        def get_dashboard():
            ...

    Args:
        timeout: int - Durée du cache en secondes

    Returns:
        Décorateur de fonction
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from flask import request

            # TODO: Implémenter avec Redis
            # cache_key = f'cache:{request.path}:{request.query_string.decode()}'
            # cached_response = redis_client.get(cache_key)
            #
            # if cached_response:
            #     return json.loads(cached_response)

            # Exécuter la fonction
            result = fn(*args, **kwargs)

            # TODO: Mettre en cache
            # redis_client.setex(cache_key, timeout, json.dumps(result))

            return result

        return wrapper
    return decorator
