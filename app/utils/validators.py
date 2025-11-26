"""
Validateurs
Validation des données selon les exigences ANSSI
"""

import re
from datetime import datetime


def validate_password(password):
    """
    [ES-102-P] Valider un mot de passe selon la politique ANSSI

    Exigences:
        - Minimum 12 caractères
        - Au moins une majuscule
        - Au moins une minuscule
        - Au moins un chiffre
        - Au moins un caractère spécial

    Args:
        password: str

    Returns:
        Tuple (bool, str) - (is_valid, error_message)
    """
    if len(password) < 12:
        return False, 'Le mot de passe doit contenir au moins 12 caractères'

    if not re.search(r'[A-Z]', password):
        return False, 'Le mot de passe doit contenir au moins une majuscule'

    if not re.search(r'[a-z]', password):
        return False, 'Le mot de passe doit contenir au moins une minuscule'

    if not re.search(r'\d', password):
        return False, 'Le mot de passe doit contenir au moins un chiffre'

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, 'Le mot de passe doit contenir au moins un caractère spécial'

    # Vérifier les patterns faibles
    common_patterns = ['123', 'abc', 'qwerty', 'password', 'admin']
    password_lower = password.lower()
    for pattern in common_patterns:
        if pattern in password_lower:
            return False, f'Le mot de passe contient un pattern courant: {pattern}'

    return True, 'Mot de passe valide'


def validate_username(username):
    """
    Valider un nom d'utilisateur

    Exigences:
        - Minimum 3 caractères
        - Maximum 32 caractères
        - Caractères alphanumériques, underscore et tiret seulement
        - Doit commencer par une lettre

    Args:
        username: str

    Returns:
        Tuple (bool, str) - (is_valid, error_message)
    """
    if not username or len(username) < 3:
        return False, 'Le nom d\'utilisateur doit contenir au moins 3 caractères'

    if len(username) > 32:
        return False, 'Le nom d\'utilisateur ne peut pas dépasser 32 caractères'

    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', username):
        return False, 'Le nom d\'utilisateur doit commencer par une lettre et contenir uniquement des caractères alphanumériques, _ ou -'

    return True, 'Nom d\'utilisateur valide'


def validate_email(email):
    """
    Valider une adresse email

    Args:
        email: str

    Returns:
        Tuple (bool, str) - (is_valid, error_message)
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not email or not re.match(email_regex, email):
        return False, 'Adresse email invalide'

    return True, 'Email valide'


def validate_serial_number(sn):
    """
    Valider un numéro de série (armes, véhicules, etc.)

    Exigences:
        - Non vide
        - Maximum 50 caractères
        - Caractères alphanumériques et tiret seulement

    Args:
        sn: str

    Returns:
        Tuple (bool, str) - (is_valid, error_message)
    """
    if not sn:
        return False, 'Le numéro de série ne peut pas être vide'

    if len(sn) > 50:
        return False, 'Le numéro de série ne peut pas dépasser 50 caractères'

    if not re.match(r'^[a-zA-Z0-9-]+$', sn):
        return False, 'Le numéro de série doit contenir uniquement des caractères alphanumériques et des tirets'

    return True, 'Numéro de série valide'


def validate_date(date_str, format='%Y-%m-%d'):
    """
    Valider et parser une date

    Args:
        date_str: str - Date au format string
        format: str - Format de la date

    Returns:
        Tuple (bool, datetime|str) - (is_valid, parsed_date|error_message)
    """
    try:
        parsed_date = datetime.strptime(date_str, format)
        return True, parsed_date
    except (ValueError, TypeError):
        return False, f'Format de date invalide. Attendu: {format}'


def validate_date_range(start_date, end_date):
    """
    Valider une plage de dates

    Args:
        start_date: datetime
        end_date: datetime

    Returns:
        Tuple (bool, str) - (is_valid, error_message)
    """
    if start_date >= end_date:
        return False, 'La date de début doit être antérieure à la date de fin'

    return True, 'Plage de dates valide'


def validate_role(role):
    """
    Valider un rôle utilisateur

    Args:
        role: str

    Returns:
        Tuple (bool, str) - (is_valid, error_message)
    """
    valid_roles = ['ADMIN', 'USER', 'READONLY', 'MODERATOR']

    if role not in valid_roles:
        return False, f'Rôle invalide. Valeurs acceptées: {", ".join(valid_roles)}'

    return True, 'Rôle valide'


def validate_status(status, entity_type):
    """
    Valider un statut selon le type d'entité

    Args:
        status: str
        entity_type: str (weapon|vehicle|mission|ammo|mre|pp)

    Returns:
        Tuple (bool, str) - (is_valid, error_message)
    """
    valid_statuses = {
        'weapon': ['AVAILABLE', 'IN_USE', 'MAINTENANCE', 'RETIRED', 'DAMAGED', 'LOST'],
        'vehicle': ['AVAILABLE', 'IN_USE', 'MAINTENANCE', 'RETIRED'],
        'mission': ['PLANNED', 'ACTIVE', 'COMPLETED', 'CANCELLED', 'POSTPONED'],
        'ammo': ['AVAILABLE', 'RESERVED', 'EXPIRED'],
        'mre': ['AVAILABLE', 'DISTRIBUTED', 'EXPIRED'],
        'pp': ['AVAILABLE', 'IN_USE', 'DAMAGED', 'RETIRED']
    }

    if entity_type not in valid_statuses:
        return False, f'Type d\'entité inconnu: {entity_type}'

    if status not in valid_statuses[entity_type]:
        return False, f'Statut invalide pour {entity_type}. Valeurs acceptées: {", ".join(valid_statuses[entity_type])}'

    return True, 'Statut valide'


def validate_quantity(quantity, min_value=0, max_value=None):
    """
    Valider une quantité

    Args:
        quantity: int
        min_value: int
        max_value: int (optional)

    Returns:
        Tuple (bool, str) - (is_valid, error_message)
    """
    try:
        qty = int(quantity)
    except (ValueError, TypeError):
        return False, 'La quantité doit être un nombre entier'

    if qty < min_value:
        return False, f'La quantité doit être au moins {min_value}'

    if max_value is not None and qty > max_value:
        return False, f'La quantité ne peut pas dépasser {max_value}'

    return True, 'Quantité valide'


def sanitize_input(input_str):
    """
    [ES-402-P] Sanitiser une entrée utilisateur pour prévenir XSS

    Args:
        input_str: str

    Returns:
        str - Input sanitisé
    """
    if not input_str:
        return input_str

    # Supprimer les caractères HTML dangereux
    dangerous_chars = ['<', '>', '"', "'", '&']
    sanitized = input_str

    for char in dangerous_chars:
        if char == '<':
            sanitized = sanitized.replace(char, '&lt;')
        elif char == '>':
            sanitized = sanitized.replace(char, '&gt;')
        elif char == '"':
            sanitized = sanitized.replace(char, '&quot;')
        elif char == "'":
            sanitized = sanitized.replace(char, '&#x27;')
        elif char == '&':
            sanitized = sanitized.replace(char, '&amp;')

    return sanitized


def validate_ip_address(ip):
    """
    Valider une adresse IP (IPv4 ou IPv6)

    Args:
        ip: str

    Returns:
        Tuple (bool, str) - (is_valid, error_message)
    """
    # IPv4 regex
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    # IPv6 regex (simplifié)
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'

    if re.match(ipv4_pattern, ip):
        # Vérifier que chaque octet est entre 0 et 255
        octets = ip.split('.')
        if all(0 <= int(octet) <= 255 for octet in octets):
            return True, 'Adresse IP valide'

    if re.match(ipv6_pattern, ip):
        return True, 'Adresse IP valide'

    return False, 'Adresse IP invalide'
