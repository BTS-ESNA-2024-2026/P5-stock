# Système de Gestion Logistique Militaire (SGLM)

Application Flask pour la gestion logistique militaire conforme aux normes ANSSI, RGS**, ISO 27001.

## 📋 Vue d'ensemble

Le SGLM est un système complet de gestion des stocks et ressources militaires incluant:

- **Gestion des utilisateurs** avec authentification MFA (TOTP)
- **Gestion des armes** (FAMAS, HK416, etc.)
- **Gestion des munitions** avec alertes de seuils
- **Gestion des véhicules** et maintenance
- **Gestion des rations** (MRE) et équipements de protection (PP)
- **Gestion des missions** avec affectation de matériel
- **Tableaux de bord** et rapports en temps réel
- **Logs d'audit** complets et immuables

## 🏗️ Architecture

```
P5-stock/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration
│   ├── api/                 # Blueprints API
│   │   ├── auth.py          # Authentification & MFA
│   │   ├── users.py         # Gestion utilisateurs
│   │   ├── weapons.py       # Gestion armes
│   │   ├── ammo.py          # Gestion munitions
│   │   ├── mre.py           # Gestion rations
│   │   ├── vehicles.py      # Gestion véhicules
│   │   ├── pp.py            # Équipements de protection
│   │   ├── missions.py      # Gestion missions
│   │   ├── logs.py          # Audit & logs
│   │   └── reports.py       # Rapports & dashboards
│   ├── models/              # Modèles de données (à implémenter avec DB)
│   ├── middleware/          # Middlewares de sécurité
│   │   ├── security.py      # Headers de sécurité ANSSI
│   │   └── auth_middleware.py # Logging des requêtes
│   └── utils/               # Utilitaires
│       ├── jwt_utils.py     # Gestion JWT avec RS256
│       ├── validators.py    # Validation des données
│       └── decorators.py    # Décorateurs RBAC
├── main.py                  # Point d'entrée
├── requirements.txt         # Dépendances Python
├── .env.example             # Template variables d'environnement
├── schema.prisma            # Schéma de base de données
└── README_FLASK.md          # Cette documentation
```

## 🚀 Installation

### Prérequis

- Python 3.11+
- pip
- virtualenv (recommandé)

### Étapes d'installation

1. **Cloner le repository**
```bash
cd /home/skyscube/Desktop/ESNA/Projet/P5-stock
```

2. **Créer un environnement virtuel**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

5. **Générer les clés RSA pour JWT**
```bash
mkdir -p keys
# Les clés seront générées automatiquement au premier lancement
```

6. **Lancer l'application**
```bash
# Développement
python main.py

# Ou avec Flask CLI
flask run

# Production (avec Gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

L'application sera accessible sur `http://localhost:5000`

## 🔐 Sécurité

### Conformité ANSSI

L'application implémente les recommandations de l'ANSSI:

- **[ES-101-P]** Hachage des mots de passe avec Argon2id/bcrypt
- **[ES-102-P]** Politique de mots de passe stricte (12+ caractères, complexité)
- **[ES-103-P]** MFA obligatoire (TOTP) pour rôles privilégiés
- **[ES-104-P]** Protection anti-brute force (5 tentatives max)
- **[ES-106-P]** JWT avec RS256 (clés RSA 4096 bits)
- **[ES-301-P]** TLS 1.3 obligatoire en production
- **[ES-405-P]** Headers de sécurité (HSTS, CSP, X-Frame-Options, etc.)
- **[ES-501-P]** Logging complet de toutes les actions

### Headers de sécurité configurés

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: no-referrer
Content-Security-Policy: default-src 'self'
```

## 📡 API Endpoints

### Authentification (`/api/v1/auth`)

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/login` | Connexion utilisateur (avec/sans MFA) |
| POST | `/verify-mfa` | Validation du code MFA |
| POST | `/refresh` | Rafraîchir le token d'accès |
| POST | `/logout` | Déconnexion |
| POST | `/setup-mfa` | Configurer MFA pour un utilisateur |
| POST | `/confirm-mfa` | Confirmer l'activation du MFA |
| GET | `/me` | Informations utilisateur connecté |

### Utilisateurs (`/api/v1/users`)

| Méthode | Route | Description | Rôle requis |
|---------|-------|-------------|-------------|
| GET | `/` | Liste des utilisateurs | ADMIN |
| GET | `/<id>` | Détails d'un utilisateur | ADMIN, self |
| POST | `/` | Créer un utilisateur | ADMIN |
| PUT | `/<id>` | Modifier un utilisateur | ADMIN |
| DELETE | `/<id>` | Désactiver un utilisateur | ADMIN |
| POST | `/<id>/change-password` | Changer le mot de passe | ADMIN, self |

### Armes (`/api/v1/weapons`)

| Méthode | Route | Description | Rôle requis |
|---------|-------|-------------|-------------|
| GET | `/` | Liste des armes | Tous |
| GET | `/<id>` | Détails d'une arme | Tous |
| POST | `/` | Enregistrer une arme | ADMIN, LOGISTICIEN |
| PUT | `/<id>` | Modifier une arme | ADMIN, LOGISTICIEN |
| PATCH | `/<id>/status` | Changer le statut | ADMIN, LOGISTICIEN |
| GET | `/alerts` | Alertes de révision | Tous |
| GET | `/types` | Types d'armes | Tous |

### Missions (`/api/v1/missions`)

| Méthode | Route | Description | Rôle requis |
|---------|-------|-------------|-------------|
| GET | `/` | Liste des missions | Tous |
| GET | `/<id>` | Détails d'une mission | Tous |
| POST | `/` | Créer une mission | ADMIN, LOGISTICIEN |
| POST | `/<id>/assign-material` | Affecter du matériel | ADMIN, LOGISTICIEN |
| PATCH | `/<id>/status` | Changer le statut | ADMIN, LOGISTICIEN |
| GET | `/<id>/report` | Générer un rapport | Tous |

### Rapports (`/api/v1/reports`)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/dashboard` | Tableau de bord KPI |
| GET | `/consumption` | Rapport de consommation |
| GET | `/forecast` | Prévisions de besoins |
| GET | `/alerts-summary` | Résumé des alertes |
| POST | `/export` | Exporter un rapport (CSV/PDF) |

## 🧪 Tests

```bash
# Installer les dépendances de test
pip install pytest pytest-flask pytest-cov

# Lancer les tests
pytest

# Avec couverture de code
pytest --cov=app tests/

# Générer un rapport HTML
pytest --cov=app --cov-report=html tests/
```

## 📊 Base de données

La base de données sera configurée avec Prisma. Le schéma est défini dans `schema.prisma`.

**Note:** Pour le moment, la DB n'est pas encore setup. Les routes API retournent des données mockées.

### Quand la DB sera prête:

1. Installer Prisma Client:
```bash
pip install prisma
```

2. Générer les modèles:
```bash
prisma generate
```

3. Appliquer les migrations:
```bash
prisma migrate dev
```

## 🔧 Configuration

Toutes les configurations sont dans `app/config.py` et `.env`:

- **SECRET_KEY**: Clé secrète Flask (changer en production)
- **JWT_SECRET_KEY**: Clé pour JWT (changer en production)
- **DATABASE_URL**: URL de connexion à la base de données
- **REDIS_URL**: URL Redis pour cache et rate limiting
- **CORS_ORIGINS**: Origines autorisées pour CORS

## 📝 Logging

Les logs sont enregistrés dans le dossier `logs/`:

- `sglm.log`: Logs applicatifs
- `security.log`: Logs de sécurité (authentification, accès, etc.)

Configuration du niveau de log dans `.env`:
```
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🎭 Rôles et Permissions (RBAC)

| Rôle | Description | Permissions |
|------|-------------|-------------|
| **ADMIN** | Administrateur système | Toutes les permissions |
| **MODERATOR** | Modérateur | Lecture/écriture, logs |
| **LOGISTICIEN** | Logisticien | Gestion stocks, véhicules, missions |
| **USER** | Utilisateur standard | Lecture seule |
| **READONLY** | Lecture seule stricte | Lecture limitée |

## 🚨 TODO / Fonctionnalités à implémenter

- [ ] Connexion à la base de données MySQL avec Prisma
- [ ] Implémentation des modèles de données
- [ ] Intégration Redis pour cache et rate limiting
- [ ] Génération de rapports PDF avec ReportLab
- [ ] Envoi d'emails pour alertes et notifications
- [ ] Tests unitaires et d'intégration complets
- [ ] Documentation API avec Swagger/OpenAPI
- [ ] Déploiement Kubernetes
- [ ] Monitoring avec Prometheus/Grafana
- [ ] Logs centralisés avec ELK Stack

## 📚 Documentation

- [Cahier des charges complet](cahier_charges_logistique_militaire.md)
- [Schéma Prisma](schema.prisma)
- Documentation API: `http://localhost:5000/api/v1/docs` (à implémenter)

## 🤝 Contribution

Ce projet suit les normes de sécurité militaires. Toute modification doit:

1. Respecter les exigences ANSSI
2. Être testée (couverture > 80%)
3. Être documentée
4. Passer les audits de sécurité

## 📄 Licence

Classification: **CONFIDENTIEL DÉFENSE**

## 🆘 Support

Pour toute question ou problème:

- Consulter la documentation complète
- Vérifier les logs dans `logs/`
- Contacter l'équipe de développement

---

**Version:** 1.0.0
**Dernière mise à jour:** 25 Novembre 2025
**Conformité:** ANSSI, RGS**, ISO 27001
