"""Public announcements API (PRD section 28, contract section 7)."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import or_

from fastapi import APIRouter

from app.api.v1.helpers import LimitQuery, count_of, published_rows
from app.core.deps import DbSession
from app.models.content import Announcement
from app.schemas.common import ListEnvelope, build_envelope
from app.schemas.content import AnnouncementOut

router = APIRouter(prefix="/announcements", tags=["announcements"])


@router.get(
    "",
    response_model=ListEnvelope[AnnouncementOut],
    summary="List active published announcements, newest first",
)
def list_announcements(
    db: DbSession,
    limit: int = LimitQuery,
) -> ListEnvelope[AnnouncementOut]:
    now = datetime.now(timezone.utc)

    stmt = published_rows(Announcement).where(
        # An expired notice is worse than no notice on an event information
        # surface - it actively misleads. Expiry is enforced at query time so a
        # notice lapses on schedule without anything having to run.
        or_(Announcement.expires_at.is_(None), Announcement.expires_at > now),
        or_(Announcement.published_at.is_(None), Announcement.published_at <= now),
    )

    total = count_of(db, stmt)
    rows = (
        db.execute(
            stmt.order_by(
                Announcement.published_at.desc().nullslast(),
                Announcement.id.desc(),
            ).limit(limit)
        )
        .scalars()
        .all()
    )
    return ListEnvelope[AnnouncementOut].model_validate(
        build_envelope(
            rows, [AnnouncementOut.model_validate(row) for row in rows], total
        )
    )
