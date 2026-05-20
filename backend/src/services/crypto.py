"""Lazy-loaded JWT keys and shared JWT constants.

Keys are read once on first use and cached in module-level state. This avoids
the per-request file I/O of the previous implementation and lets the app crash
fast at first login if the private/public key pair is missing.
"""
from __future__ import annotations

import os
from pathlib import Path

JWT_ALGORITHM = 'RS256'
JWT_ISSUER = os.getenv('JWT_ISSUER', 'p5stock')
JWT_AUDIENCE = os.getenv('JWT_AUDIENCE', 'p5stock-api')

# Paths can be overridden via env (useful in containers where keys are mounted
# at /run/secrets/jwt_private.pem etc.). They default to the project root.
_PRIVATE_PATH = Path(os.getenv('JWT_PRIVATE_KEY_PATH', 'private.pem'))
_PUBLIC_PATH = Path(os.getenv('JWT_PUBLIC_KEY_PATH', 'public.pem'))

_private_key: bytes | None = None
_public_key: bytes | None = None


def _read(path: Path, label: str) -> bytes:
    if not path.exists():
        raise FileNotFoundError(
            f"JWT {label} key not found at {path}. Generate the keypair with "
            f"`pnpm genkey` or mount it through the {label.upper()}_KEY_PATH env var."
        )
    return path.read_bytes()


def get_private_key() -> bytes:
    global _private_key
    if _private_key is None:
        _private_key = _read(_PRIVATE_PATH, 'private')
    return _private_key


def get_public_key() -> bytes:
    global _public_key
    if _public_key is None:
        _public_key = _read(_PUBLIC_PATH, 'public')
    return _public_key
