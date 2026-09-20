"""Authentication schemas (contract section 8)."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    """JSON body, not form-encoded - the contract is explicit about this."""

    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)


class UserOut(BaseModel):
    """
    The public shape of a user. Note what is absent: `hashed_password` is not a
    field here, so no code path can accidentally serialise a credential.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut
