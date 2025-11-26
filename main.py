"""
Point d'entrée de l'application Flask
Système de Gestion Logistique Militaire (SGLM)

Usage:
    Development:
        flask run
        ou
        python main.py

    Production:
        gunicorn -w 4 -b 0.0.0.0:5000 main:app
"""

import os
from app import create_app

# Créer l'application Flask
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Paramètres de développement
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║  Système de Gestion Logistique Militaire (SGLM)          ║
    ║  Version: 1.0.0                                           ║
    ║  Environment: {os.getenv('FLASK_ENV', 'development')}
    ║  API: http://{host}:{port}/api/v1
    ║  Health: http://{host}:{port}/health
    ╚═══════════════════════════════════════════════════════════╝
    """)

    app.run(host=host, port=port, debug=debug)
