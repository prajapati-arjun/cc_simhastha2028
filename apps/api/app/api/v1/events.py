"""Public events API (PRD section 8, contract section 1)."""
from __future__ import annotations

from datetime import date, datetime, time, timezone

from fastapi import APIRouter, HTTPException, Query, status

from app.api.v1.helpers import LimitQuery, OffsetQuery, count_of, published_rows
from app.core.deps import DbSession
from app.models.content import Event
from app.models.enums import EventCategory
from app.schemas.common import ListEnvelope, build_envelope
from app.schemas.content import EventOut

router = APIRouter(prefix="/events", tags=["events"])


@router.get(
    "",
    response_model=ListEnvelope[EventOut],
    summary="List published Simhastha calendar events",
)
def list_events(
    db: DbSession,
    category: EventCategory | None = Query(
        default=None, description="Filter by event category."
    ),
    from_date: date | None = Query(
        default=None, description="Only events starting on or after this date (UTC)."
    ),
    to_date: date | None = Query(
        default=None, description="Only events starting on or before this date (UTC)."
    ),
    limit: int = LimitQuery,
    offset: int = OffsetQuery,
) -> ListEnvelope[EventOut]:
    stmt = published_rows(Event)

    if category is not None:
        stmt = stmt.where(Event.category == category.value)
    if from_date is not None:
        stmt = stmt.where(
            Event.starts_at >= datetime.combine(from_date, time.min, tzinfo=timezone.utc)
        )
    if to_date is not None:
        # Inclusive upper bound: `to_date` names a whole day, so an event at
        # 23:00 on that day must still be returned.
        stmt = stmt.where(
            Event.starts_at <= datetime.combine(to_date, time.max, tzinfo=timezone.utc)
        )

    total = count_of(db, stmt)
    rows = (
        db.execute(stmt.order_by(Event.starts_at.asc()).limit(limit).offset(offset))
        .scalars()
        .all()
    )
    return ListEnvelope[EventOut].model_validate(
        build_envelope(rows, [EventOut.model_validate(row) for row in rows], total)
    )


@router.get(
    "/{slug}",
    response_model=EventOut,
    summary="Get one published event by slug",
    responses={404: {"description": "No published event with that slug."}},
)
def get_event(slug: str, db: DbSession) -> EventOut:
    row = db.execute(
        published_rows(Event).where(Event.slug == slug)
    ).scalar_one_or_none()
    if row is None:
        # Drafts are reported as 404 rather than 403: whether an unpublished
        # event exists is itself non-public information.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    return EventOut.model_validate(row)
