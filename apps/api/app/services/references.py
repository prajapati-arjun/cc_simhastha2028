"""Collision-safe allocation of opaque case references."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import generate_case_reference

_MAX_ATTEMPTS = 8


class CaseReferenceExhausted(RuntimeError):
    """Raised if we cannot find a free reference - should never happen."""


def allocate_case_reference(db: Session, model: type, prefix: str) -> str:
    """
    Draw a random reference and confirm it is unused.

    The uniqueness check here is a courtesy, not the guarantee: every
    `case_reference` column carries a UNIQUE index, so a race between two
    concurrent submissions still fails closed at the database rather than
    silently handing two reporters the same key to each other's case.
    """
    for _ in range(_MAX_ATTEMPTS):
        candidate = generate_case_reference(prefix)
        exists = db.execute(
            select(model.id).where(model.case_reference == candidate).limit(1)
        ).first()
        if exists is None:
            return candidate
    raise CaseReferenceExhausted(
        f"Could not allocate a unique {prefix} reference after {_MAX_ATTEMPTS} attempts"
    )
