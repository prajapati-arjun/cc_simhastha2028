"""Query helpers shared by the public and admin routers."""
from __future__ import annotations

from typing import Any

from fastapi import Query
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.enums import ContentStatus

LimitQuery = Query(
    default=settings.DEFAULT_PAGE_LIMIT,
    ge=1,
    le=settings.MAX_PAGE_LIMIT,
    description="Maximum rows to return.",
)
OffsetQuery = Query(default=0, ge=0, description="Rows to skip.")


def live_rows(model: type) -> Select:
    """Base SELECT excluding soft-deleted rows."""
    stmt = select(model)
    if hasattr(model, "deleted_at"):
        stmt = stmt.where(model.deleted_at.is_(None))
    return stmt


def published_rows(model: type) -> Select:
    """
    Base SELECT for PUBLIC endpoints.

    Contract section 0: public endpoints return published rows only. Drafts are
    unreviewed content and are visible solely through an authenticated admin
    route. Every public list and detail handler starts from this helper so the
    filter cannot be forgotten on a new endpoint.
    """
    return live_rows(model).where(model.status == ContentStatus.PUBLISHED.value)


def count_of(db: Session, stmt: Select) -> int:
    """Total matching rows, ignoring limit/offset."""
    subquery = stmt.order_by(None).subquery()
    return int(db.execute(select(func.count()).select_from(subquery)).scalar_one())


def apply_updates(instance: Any, payload: dict[str, Any], skip: set[str] | None = None) -> list[str]:
    """
    Copy a validated partial-update payload onto an ORM instance.

    Returns the names of fields that actually changed, which is what the audit
    detail records (never the values - see app/services/audit.py).
    """
    skip = skip or set()
    changed: list[str] = []
    for field, value in payload.items():
        if field in skip:
            continue
        if getattr(instance, field, None) != value:
            setattr(instance, field, value)
            changed.append(field)
    return changed
