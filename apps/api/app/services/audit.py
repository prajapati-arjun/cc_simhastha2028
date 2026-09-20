"""
Audit-trail writer (PRD section 16, section 30).

One helper, used by every admin write and every public safety-critical
submission, so there is a single place to reason about what gets recorded.

Data minimisation (PRD section 31): `detail` records *which* fields were
touched and non-identifying metadata (category, status transition). It never
records the value of a personal field - no names, phone numbers, physical
descriptions, photo URLs or precise coordinates reach the audit table. The
audit trail answers "who changed what, when", not "what did the reporter say".
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.audit import AuditLog

#: Never copy the value of these columns into an audit detail blob.
SENSITIVE_FIELDS: frozenset[str] = frozenset(
    {
        "person_name",
        "person_age",
        "person_gender",
        "physical_description",
        "photo_url",
        "reporter_name",
        "reporter_phone",
        "reporter_relationship",
        "description",
        "location_text",
        "last_seen_location_text",
        "latitude",
        "longitude",
        "note",
        "hashed_password",
        "password",
        "email",
    }
)


def redact(payload: dict[str, Any]) -> dict[str, Any]:
    """Replace sensitive values with a presence marker."""
    return {
        key: ("[redacted]" if key in SENSITIVE_FIELDS and value is not None else value)
        for key, value in payload.items()
    }


def record_audit(
    db: Session,
    *,
    action: str,
    entity_type: str,
    entity_id: str | int | None = None,
    actor_user_id: int | None = None,
    detail: dict[str, Any] | None = None,
) -> AuditLog:
    """
    Append an audit row to the current session.

    The row is flushed but NOT committed: it joins the caller's transaction, so
    an audit entry can never survive a submission that was itself rolled back,
    and a successful write can never lose its audit entry.
    """
    entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        detail=redact(detail) if detail else None,
    )
    db.add(entry)
    db.flush()
    return entry
