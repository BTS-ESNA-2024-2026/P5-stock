"""
Utilitaires pour le hachage et la vérification des mots de passe
Conformité ANSSI: ES-101-P (Argon2id)
"""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash
import secrets


# Configuration Argon2 selon recommandations ANSSI
ph = PasswordHasher(
    time_cost=3,        # Nombre d'itérations
    memory_cost=65536,  # 64 MB de mémoire
    parallelism=4,      # 4 threads parallèles
    hash_len=32,        # Longueur du hash: 32 bytes
    salt_len=16         # Longueur du sel: 16 bytes
)


def hash_password(password):
    """
    [ES-101-P] Hacher un mot de passe avec Argon2id
    Recommandation ANSSI pour le hachage des mots de passe

    Args:
        password: str - Mot de passe en clair

    Returns:
        tuple (hash_str, algorithm) - Hash et nom de l'algorithme
    """
    hash_str = ph.hash(password)
    algorithm = 'ARGON2ID'

    return hash_str, algorithm


def verify_password(password, hash_str):
    """
    [ES-101-P] Vérifier un mot de passe contre son hash

    Args:
        password: str - Mot de passe en clair
        hash_str: str - Hash Argon2

    Returns:
        bool - True si le mot de passe correspond
    """
    try:
        ph.verify(hash_str, password)

        # Vérifier si le hash doit être mis à jour (paramètres changés)
        if ph.check_needs_rehash(hash_str):
            # TODO: Mettre à jour le hash en base de données
            pass

        return True

    except (VerifyMismatchError, VerificationError, InvalidHash):
        return False


def generate_secure_password(length=16):
    """
    Générer un mot de passe sécurisé aléatoire

    Args:
        length: int - Longueur du mot de passe (minimum 12)

    Returns:
        str - Mot de passe généré
    """
    if length < 12:
        length = 12

    # Générer un mot de passe avec des caractères variés
    import string
    alphabet = string.ascii_letters + string.digits + string.punctuation

    # Assurer qu'on a au moins un de chaque type
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation)
    ]

    # Compléter avec des caractères aléatoires
    password += [secrets.choice(alphabet) for _ in range(length - 4)]

    # Mélanger
    secrets.SystemRandom().shuffle(password)

    return ''.join(password)


def generate_reset_token():
    """
    Générer un token sécurisé pour la réinitialisation de mot de passe

    Returns:
        str - Token hexadécimal
    """
    return secrets.token_urlsafe(32)
