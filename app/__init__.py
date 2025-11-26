"""
Application Flask - Système de Gestion Logistique Militaire (SGLM)
Initialisation de l'application et des extensions
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
import logging
from logging.handlers import RotatingFileHandler

from app.config import config


def create_app(config_name=None):
    """
    Factory pattern pour créer l'application Flask

    Args:
        config_name: Nom de la configuration à utiliser (development, production, testing)

    Returns:
        Flask application instance
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialiser les extensions
    initialize_extensions(app)

    # Configurer le logging
    configure_logging(app)

    # Enregistrer les blueprints
    register_blueprints(app)

    # Enregistrer les middlewares
    register_middlewares(app)

    # Enregistrer les gestionnaires d'erreurs
    register_error_handlers(app)

    # Route de santé
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'version': app.config['API_VERSION']}), 200

    return app


def initialize_extensions(app):
    """Initialise les extensions Flask"""

    # CORS
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

    # JWT Manager
    jwt = JWTManager(app)

    # Gestionnaires JWT personnalisés
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'token_expired',
            'message': 'Le token a expiré'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'invalid_token',
            'message': 'Signature de vérification invalide'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'authorization_required',
            'message': 'Token d\'autorisation manquant'
        }), 401

    # Database initialization
    from app.database import init_db, close_db
    init_db(app)
    app.teardown_appcontext(close_db)

    # Redis pour le cache et rate limiting (à activer plus tard)
    # from flask_limiter import Limiter
    # from flask_limiter.util import get_remote_address
    # limiter = Limiter(
    #     app,
    #     key_func=get_remote_address,
    #     storage_uri=app.config['RATELIMIT_STORAGE_URL']
    # )


def configure_logging(app):
    """Configure le système de logging"""

    if not app.debug and not app.testing:
        # Créer le dossier de logs s'il n'existe pas
        if not os.path.exists(app.config['LOG_DIR']):
            os.mkdir(app.config['LOG_DIR'])

        # Handler pour les logs applicatifs
        file_handler = RotatingFileHandler(
            os.path.join(app.config['LOG_DIR'], 'sglm.log'),
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        # Handler pour les logs de sécurité (audit)
        security_handler = RotatingFileHandler(
            os.path.join(app.config['LOG_DIR'], 'security.log'),
            maxBytes=10240000,
            backupCount=50  # Conservation plus longue pour l'audit
        )
        security_handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
        security_handler.setLevel(logging.WARNING)
        app.logger.addHandler(security_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('SGLM startup')


def register_blueprints(app):
    """Enregistre tous les blueprints de l'application"""

    from app.api import auth, users, assets_generic, missions, logs, reports, web

    api_prefix = app.config['API_PREFIX']

    # Enregistrer les blueprints API
    app.register_blueprint(auth.bp, url_prefix=f'{api_prefix}/auth')
    app.register_blueprint(users.bp, url_prefix=f'{api_prefix}/users')
    app.register_blueprint(assets_generic.bp, url_prefix=f'{api_prefix}/assets')
    app.register_blueprint(missions.bp, url_prefix=f'{api_prefix}/missions')
    app.register_blueprint(logs.bp, url_prefix=f'{api_prefix}/logs')
    app.register_blueprint(reports.bp, url_prefix=f'{api_prefix}/reports')

    # Enregistrer le blueprint web (frontend)
    app.register_blueprint(web.bp)


def register_middlewares(app):
    """Enregistre les middlewares personnalisés"""

    from app.middleware.security import security_headers_middleware
    from app.middleware.auth_middleware import log_request_middleware

    app.before_request(log_request_middleware)
    app.after_request(security_headers_middleware)


def register_error_handlers(app):
    """Enregistre les gestionnaires d'erreurs personnalisés"""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'bad_request',
            'message': 'Requête invalide'
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'unauthorized',
            'message': 'Non autorisé'
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'forbidden',
            'message': 'Accès interdit'
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'not_found',
            'message': 'Ressource non trouvée'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Erreur serveur: {error}')
        return jsonify({
            'error': 'internal_error',
            'message': 'Erreur interne du serveur'
        }), 500
