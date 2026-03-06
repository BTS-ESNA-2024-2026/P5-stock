from flask import request, jsonify
from loguru import logger
from src.services.tools import jwt_decode


def register_middleware(app):
    """Register middleware hooks with the Flask app."""

    # Tes middlewares existants
    app.before_request(get_jwt)

    # Gestionnaire d'erreur pour rate limit (optionnel mais recommandé)
    @app.errorhandler(429)
    def ratelimit_error(e):
        logger.warning(
            f"Rate limit exceeded: {request.remote_addr} on {request.path}"
        )
        return jsonify({
            'error': 'Too many requests',
            'message': 'Please slow down and try again later'
        }), 429

def get_jwt():
    access_token = request.cookies.get('access_token')
    if not access_token:
        request.current_user = None
        return None
    user = jwt_decode(request)
    request.current_user = user
    return None
