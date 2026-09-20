"""
Password hashing, JWT issuance/verification, and opaque case-reference
generation.

Case references are the single most privacy-sensitive primitive in this
service: they are the only key to a lost-child or lost-property report, so they
must be unguessable. See generate_case_reference().
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#: Unambiguous alphabet: no 0/O and no 1/I/L, so a reference read off a phone
#: screen, spoken to a help-desk volunteer, or written on paper survives the
#: round trip. 31 symbols over 8 positions is ~39.6 bits of entropy.
CASE_REFERENCE_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
CASE_REFERENCE_LENGTH = 8


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_case_reference(prefix: str) -> str:
    """
    Build an opaque case reference, e.g. ``LF-3N8P2VQ7``.

    Deliberately NOT derived from the primary key and NOT sequential: a
    sequential or id-derived reference would let anyone holding one valid
    reference walk the whole table of missing-person reports at an event
    serving millions of pilgrims (decision D-01, PRD section 31 data
    minimisation). ``secrets.choice`` draws from the OS CSPRNG.
    """
    body = "".join(
        secrets.choice(CASE_REFERENCE_ALPHABET) for _ in range(CASE_REFERENCE_LENGTH)
    )
    return f"{prefix}-{body}"


def create_access_token(
    subject: str | int,
    role: str,
    expires_delta: timedelta | None = None,
) -> tuple[str, int]:
    """Return ``(encoded_jwt, expires_in_seconds)``."""
    expires_delta = expires_delta or timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, int(expires_delta.total_seconds())


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and verify a bearer token. Returns None on any failure."""
    try:
        return jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        return None
