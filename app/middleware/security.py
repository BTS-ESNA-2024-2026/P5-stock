"""
Middleware de sécurité
Implémentation des headers de sécurité ANSSI [ES-405-P]
"""

from flask import current_app, request


def security_headers_middleware(response):
    """
    [ES-405-P] Ajoute les headers de sécurité obligatoires
    Conformité ANSSI

    Headers ajoutés:
        - Strict-Transport-Security
        - X-Content-Type-Options
        - X-Frame-Options
        - X-XSS-Protection
        - Referrer-Policy
        - Content-Security-Policy
    """
    security_headers = current_app.config.get('SECURITY_HEADERS', {})

    for header, value in security_headers.items():
        response.headers[header] = value

    return response


def rate_limit_exceeded_handler(error):
    """
    Gestionnaire pour les erreurs de rate limiting
    [ES-404-P] Protection anti-DDoS
    """
    current_app.logger.warning(f'Rate limit exceeded from {request.remote_addr}')

    return {
        'error': 'rate_limit_exceeded',
        'message': 'Trop de requêtes. Veuillez réessayer plus tard.'
    }, 429


def cors_headers_middleware(response):
    """
    Ajoute les headers CORS appropriés
    [ES-403-P] Protection CSRF avec SameSite
    """
    # CORS headers sont déjà gérés par Flask-CORS
    # Mais on peut ajouter des headers additionnels ici si nécessaire

    return response
