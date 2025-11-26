"""
Utilitaires JWT
Gestion des tokens JWT avec RS256 (RSA 4096 bits)
[ES-106-P] Conformité ANSSI
"""

import jwt
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import os


def generate_rsa_keys():
    """
    [ES-106-P] Générer une paire de clés RSA 4096 bits
    Recommandation ANSSI

    Returns:
        Tuple (private_key_pem, public_key_pem)
    """
    # Générer la clé privée
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )

    # Encoder la clé privée en PEM
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Extraire et encoder la clé publique
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem.decode('utf-8'), public_pem.decode('utf-8')


def load_rsa_keys():
    """
    Charger les clés RSA depuis des fichiers ou variables d'environnement

    Returns:
        Tuple (private_key, public_key)
    """
    # En production, les clés doivent être stockées dans HashiCorp Vault
    # Pour le développement, on peut les charger depuis des fichiers

    private_key_path = os.getenv('JWT_PRIVATE_KEY_PATH', 'keys/jwt_private.pem')
    public_key_path = os.getenv('JWT_PUBLIC_KEY_PATH', 'keys/jwt_public.pem')

    try:
        with open(private_key_path, 'r') as f:
            private_key = f.read()
        with open(public_key_path, 'r') as f:
            public_key = f.read()
    except FileNotFoundError:
        # Si les clés n'existent pas, en générer de nouvelles (dev seulement)
        print("Warning: JWT keys not found, generating new ones...")
        private_key, public_key = generate_rsa_keys()

        # Créer le dossier keys s'il n'existe pas
        os.makedirs('keys', exist_ok=True)

        # Sauvegarder les clés
        with open(private_key_path, 'w') as f:
            f.write(private_key)
        with open(public_key_path, 'w') as f:
            f.write(public_key)

    return private_key, public_key


def create_token(identity, expires_delta=None, token_type='access'):
    """
    Créer un token JWT signé avec RS256

    Args:
        identity: dict - Informations de l'utilisateur
        expires_delta: timedelta - Durée de validité
        token_type: str - Type de token (access ou refresh)

    Returns:
        str - Token JWT encodé
    """
    private_key, _ = load_rsa_keys()

    if expires_delta is None:
        expires_delta = timedelta(minutes=30)

    payload = {
        'identity': identity,
        'type': token_type,
        'exp': datetime.utcnow() + expires_delta,
        'iat': datetime.utcnow(),
        'jti': generate_jti()  # JWT ID unique pour blacklist
    }

    token = jwt.encode(payload, private_key, algorithm='RS256')

    return token


def decode_token(token):
    """
    Décoder et vérifier un token JWT

    Args:
        token: str - Token JWT encodé

    Returns:
        dict - Payload du token

    Raises:
        jwt.ExpiredSignatureError: Token expiré
        jwt.InvalidTokenError: Token invalide
    """
    _, public_key = load_rsa_keys()

    payload = jwt.decode(token, public_key, algorithms=['RS256'])

    return payload


def generate_jti():
    """
    Générer un JWT ID unique pour le tracking et la blacklist

    Returns:
        str - UUID unique
    """
    import uuid
    return str(uuid.uuid4())


def verify_token_signature(token):
    """
    Vérifier uniquement la signature d'un token sans valider l'expiration

    Args:
        token: str - Token JWT

    Returns:
        bool - True si signature valide
    """
    try:
        _, public_key = load_rsa_keys()
        jwt.decode(token, public_key, algorithms=['RS256'], options={'verify_exp': False})
        return True
    except jwt.InvalidTokenError:
        return False
