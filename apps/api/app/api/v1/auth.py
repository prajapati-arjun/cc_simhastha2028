"""Authentication API (PRD section 29, contract section 8)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import CurrentUser, DbSession
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserOut
from app.services.audit import record_audit

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=user.role_name,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Exchange credentials for a bearer token",
    description=(
        "Accepts a JSON body (not form-encoded). Returns an HS256 JWT whose "
        "claims carry the user id (`sub`), `role` and `exp`."
    ),
    responses={401: {"description": "Invalid username or password."}},
)
def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    user = db.execute(
        select(User).where(
            User.username == payload.username, User.deleted_at.is_(None)
        )
    ).scalar_one_or_none()

    # One message and one code for "no such user", "wrong password" and
    # "deactivated account". Distinguishing them would let an unauthenticated
    # caller enumerate valid administrator usernames.
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if user is None or not user.is_active:
        raise invalid
    if not verify_password(payload.password, user.hashed_password):
        record_audit(
            db,
            action="auth.login_failed",
            entity_type="user",
            entity_id=user.id,
            actor_user_id=None,
            detail={"username": user.username, "reason": "bad_password"},
        )
        db.commit()
        raise invalid

    token, expires_in = create_access_token(subject=user.id, role=user.role_name)

    record_audit(
        db,
        action="auth.login",
        entity_type="user",
        entity_id=user.id,
        actor_user_id=user.id,
        detail={"username": user.username, "role": user.role_name},
    )
    db.commit()

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        user=_user_out(user),
    )


@router.get(
    "/me",
    response_model=UserOut,
    summary="Return the authenticated user",
    responses={401: {"description": "Missing, malformed or expired token."}},
)
def read_me(current_user: CurrentUser) -> UserOut:
    return _user_out(current_user)
