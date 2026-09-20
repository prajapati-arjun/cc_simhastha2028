"""
Command Center aggregation (PRD section 24).

Reads only - this module never writes to LostFoundCase, MissingPersonCase or
SosIncident, and never modifies app/models/cases.py (owned by the
incident/lost-found-matching agent this sprint). It queries those tables
exactly the way the public/admin routers already do.

"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.helpers import published_rows
from app.core.notices import COMMAND_CENTER_NOTICE
from app.models.cases import LostFoundCase, MissingPersonCase
from app.models.content import Announcement
from app.models.emergency import SosIncident
from app.models.enums import AnnouncementPriority, LostFoundStatus, MissingPersonStatus
from app.schemas.command_center import (
    CommandCenterCaseTotalsOut,
    CommandCenterCriticalAlertOut,
    CommandCenterDecisionOut,
    CommandCenterHumanDecisionsOut,
    CommandCenterObservedOut,
    CommandCenterOverviewOut,
    CommandCenterRecommendationsOut,
    CommandCenterZoneOut,
)
from app.schemas.crowd import CrowdReadingOut
from app.services.crowd import list_zone_summaries

#: SosIncident (app/models/emergency.py) has no admin-editable status
#: workflow yet - every row is created with status="recorded" and there is
#: no transition table analogous to LOST_FOUND_TRANSITIONS /
#: MISSING_PERSON_TRANSITIONS (app/services/workflow.py). These values are
#: forward-compatible placeholders should that change; today every incident
#: is open under this definition.
CLOSED_SOS_STATUSES: frozenset[str] = frozenset({"closed", "resolved"})

_OPEN_LOST_FOUND_EXCLUDED = frozenset(
    {LostFoundStatus.CLOSED.value, LostFoundStatus.REJECTED.value}
)
_OPEN_MISSING_PERSON_EXCLUDED = frozenset(
    {MissingPersonStatus.RESOLVED.value, MissingPersonStatus.CLOSED.value}
)

#: Cap on how many recent case-status rows feed the human-decisions section.
RECENT_DECISIONS_LIMIT = 20

CASE_TOTALS_NOTE = (
    "Platform-wide totals, not per zone: SOS, lost-found and missing-person "
    "records do not carry a zone reference in this prototype's schema, so "
    "attributing them to a zone would mean fabricating a spatial match this "
    "sprint's seed data cannot honestly support."
)
RECOMMENDATIONS_NOTE = (
    "Not available in this prototype. No model-generated recommendation "
    "engine exists; this section is intentionally left empty rather than "
    "simulated."
)
HUMAN_DECISIONS_NOTE = (
    "Every status below was set by an authenticated admin action, not "
    "generated or inferred by any model. It reflects a human decision "
    "recorded at the time shown."
)


def _open_count(db: Session, model: type, excluded_statuses: frozenset[str]) -> int:
    stmt = select(model.id).where(model.status.notin_(excluded_statuses))
    return len(db.execute(stmt).all())


def _critical_announcements(
    db: Session, now: datetime
) -> list[CommandCenterCriticalAlertOut]:
    stmt = published_rows(Announcement).where(
        Announcement.priority == AnnouncementPriority.CRITICAL.value
    )
    rows = db.execute(stmt.order_by(Announcement.published_at.desc())).scalars().all()
    active = [row for row in rows if row.expires_at is None or row.expires_at > now]
    return [
        CommandCenterCriticalAlertOut(
            id=row.id,
            slug=row.slug,
            title=row.title,
            body=row.body,
            priority=row.priority,
            published_at=row.published_at,
            expires_at=row.expires_at,
        )
        for row in active
    ]


def _recent_decisions(db: Session) -> list[CommandCenterDecisionOut]:
    decisions: list[CommandCenterDecisionOut] = []
    for entity_type, model in (
        ("sos_incident", SosIncident),
        ("lost_found_case", LostFoundCase),
        ("missing_person_case", MissingPersonCase),
    ):
        rows = (
            db.execute(
                select(model)
                .order_by(model.updated_at.desc())
                .limit(RECENT_DECISIONS_LIMIT)
            )
            .scalars()
            .all()
        )
        decisions.extend(
            CommandCenterDecisionOut(
                entity_type=entity_type,
                case_reference=row.case_reference,
                status=row.status,
                updated_at=row.updated_at,
            )
            for row in rows
        )
    decisions.sort(key=lambda decision: decision.updated_at, reverse=True)
    return decisions[:RECENT_DECISIONS_LIMIT]


def build_overview(db: Session) -> CommandCenterOverviewOut:
    now = datetime.now(timezone.utc)

    zones, latest_by_zone = list_zone_summaries(db)
    zone_rows = [
        CommandCenterZoneOut(
            zone_id=zone.id,
            zone_slug=zone.slug,
            zone_name=zone.name,
            zone_type=zone.zone_type,
            latest_crowd_reading=(
                CrowdReadingOut.model_validate(latest_by_zone[zone.id])
                if zone.id in latest_by_zone
                else None
            ),
        )
        for zone in zones
    ]

    observed = CommandCenterObservedOut(
        zones=zone_rows,
        case_totals=CommandCenterCaseTotalsOut(
            open_sos_incidents=_open_count(db, SosIncident, CLOSED_SOS_STATUSES),
            open_lost_found_cases=_open_count(
                db, LostFoundCase, _OPEN_LOST_FOUND_EXCLUDED
            ),
            open_missing_person_cases=_open_count(
                db, MissingPersonCase, _OPEN_MISSING_PERSON_EXCLUDED
            ),
        ),
        case_totals_note=CASE_TOTALS_NOTE,
        critical_announcements=_critical_announcements(db, now),
    )

    recommendations = CommandCenterRecommendationsOut(
        available=False, items=[], note=RECOMMENDATIONS_NOTE
    )

    human_decisions = CommandCenterHumanDecisionsOut(
        note=HUMAN_DECISIONS_NOTE,
        recent_status_decisions=_recent_decisions(db),
    )

    return CommandCenterOverviewOut(
        generated_at=now,
        prototype_notice=COMMAND_CENTER_NOTICE,
        observed=observed,
        recommendations=recommendations,
        human_decisions=human_decisions,
    )
