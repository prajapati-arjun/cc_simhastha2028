"""
Shared FastAPI dependencies: DB session, current user, and role gating.

RBAC posture (PRD section 29 - least privilege, auditable authorization):
authorisation is a dependency on the router, not an `if` inside each handler,
so a new admin endpoint cannot be added without a role check.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.enums import ADMIN_ROLE_NAMES
from app.models.user import User

#: auto_error=False so a missing header yields our own 401 with a useful
#: message rather than FastAPI's bare 403.
bearer_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]

_UNAUTHENTICATED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    db: DbSession,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ] = None,
) -> User:
    """Resolve the bearer token to a live, active user."""
    if credentials is None or not credentials.credentials:
        raise _UNAUTHENTICATED

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise _UNAUTHENTICATED

    subject = payload.get("sub")
    if subject is None:
        raise _UNAUTHENTICATED
    try:
        user_id = int(subject)
    except (TypeError, ValueError):
        raise _UNAUTHENTICATED from None

    user = db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    ).scalar_one_or_none()

    # A token stays cryptographically valid until it expires, so deactivation
    # and deletion are re-checked here on every request rather than trusted
    # from the claims.
    if user is None or not user.is_active:
        raise _UNAUTHENTICATED
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_admin(current_user: CurrentUser) -> User:
    """
    Gate for every /api/v1/admin/* route.

    Sprint 1 admits super_admin and content_manager. public_user is rejected
    with 403 (authenticated, but not permitted) rather than 401, so the client
    can tell "log in" from "your account cannot do this".
    """
    if current_user.role_name not in ADMIN_ROLE_NAMES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Your role does not permit access to the administration API."
            ),
        )
    return current_user


AdminUser = Annotated[User, Depends(require_admin)]
