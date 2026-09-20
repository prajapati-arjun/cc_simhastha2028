"""
Crowd Analytics service (PRD section 10, section 26).
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql import func as sql_func

from app.api.v1.helpers import live_rows
from app.core.notices import CROWD_NOTICE
from app.models.content import Zone
from app.models.crowd import CrowdReading
from app.models.user import User
from app.schemas.crowd import CrowdReadingCreate
from app.services.audit import record_audit

#: History rows returned by GET /crowd/zones/{zone_ref} when no explicit
#: limit is requested.
DEFAULT_HISTORY_LIMIT = 20


def resolve_zone(db: Session, zone_ref: str) -> Zone | None:
    """Look a zone up by numeric id or by slug (same convention as ghats)."""
    stmt = live_rows(Zone)
    if zone_ref.isdigit():
        stmt = stmt.where(Zone.id == int(zone_ref))
    else:
        stmt = stmt.where(Zone.slug == zone_ref)
    return db.execute(stmt).scalar_one_or_none()


def _latest_readings_by_zone(
    db: Session, zone_ids: list[int]
) -> dict[int, CrowdReading]:
    """One query returning the single latest reading per zone id, via a
    row_number() window rather than N queries or N+1 round trips."""
    if not zone_ids:
        return {}

    row_number = (
        sql_func.row_number()
        .over(
            partition_by=CrowdReading.zone_id,
            order_by=CrowdReading.recorded_at.desc(),
        )
        .label("rn")
    )
    subq = (
        select(CrowdReading, row_number)
        .where(CrowdReading.zone_id.in_(zone_ids))
        .subquery()
    )
    reading_alias = aliased(CrowdReading, subq)
    rows = (
        db.execute(select(reading_alias).where(subq.c.rn == 1)).scalars().all()
    )
    return {row.zone_id: row for row in rows}


def list_zone_summaries(db: Session) -> tuple[list[Zone], dict[int, CrowdReading]]:
    """All live zones plus, for each, its single latest reading (if any)."""
    zones = db.execute(live_rows(Zone).order_by(Zone.id)).scalars().all()
    latest_by_zone = _latest_readings_by_zone(db, [z.id for z in zones])
    return list(zones), latest_by_zone


def get_zone_with_history(
    db: Session, zone_ref: str, history_limit: int = DEFAULT_HISTORY_LIMIT
) -> tuple[Zone, CrowdReading | None, list[CrowdReading]] | None:
    """Resolve a zone and return it with its most recent readings, newest first."""
    zone = resolve_zone(db, zone_ref)
    if zone is None:
        return None

    history = (
        db.execute(
            select(CrowdReading)
            .where(CrowdReading.zone_id == zone.id)
            .order_by(CrowdReading.recorded_at.desc())
            .limit(history_limit)
        )
        .scalars()
        .all()
    )
    latest = history[0] if history else None
    return zone, latest, list(history)


def record_reading(
    db: Session, zone: Zone, payload: CrowdReadingCreate, admin_user: User
) -> CrowdReading:
    """
    Persist one operator-entered observation and its audit trail.

    Nothing here reads from, or writes to, any external system - the admin
    calling this endpoint IS the source of the number (PRD section 26).
    """
    reading = CrowdReading(
        zone_id=zone.id,
        density_level=payload.density_level.value,
        estimated_count_band=(
            payload.estimated_count_band.value
            if payload.estimated_count_band is not None
            else None
        ),
        source=payload.source.value,
        recorded_at=payload.recorded_at or datetime.now(timezone.utc),
        recorded_by_user_id=admin_user.id,
    )
    db.add(reading)
    db.flush()

    record_audit(
        db,
        action="crowd_reading.recorded",
        entity_type="crowd_reading",
        entity_id=reading.id,
        actor_user_id=admin_user.id,
        detail={
            "zone_id": zone.id,
            "zone_slug": zone.slug,
            "density_level": reading.density_level,
            "estimated_count_band": reading.estimated_count_band,
            "source": reading.source,
        },
    )
    db.commit()
    db.refresh(reading)
    return reading
