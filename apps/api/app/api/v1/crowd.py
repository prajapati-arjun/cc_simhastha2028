"""
Crowd Analytics API (PRD section 10, section 26).

Every reading exposed here is an operator-entered observation, never a live
CCTV, sensor or headcount feed, and every figure is an aggregate zone-level
band - not a per-person count (no biometrics, no facial recognition, ever).
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.core.deps import AdminUser, DbSession
from app.schemas.common import ListEnvelope
from app.schemas.crowd import (
    CrowdReadingCreate,
    CrowdReadingCreatedOut,
    CrowdReadingOut,
    CrowdZoneDetailOut,
    CrowdZoneSummaryOut,
)
from app.services.crowd import (
    CROWD_NOTICE,
    DEFAULT_HISTORY_LIMIT,
    get_zone_with_history,
    list_zone_summaries,
    record_reading,
    resolve_zone,
)

router = APIRouter(prefix="/crowd", tags=["crowd"])


def _summary_out(zone, reading) -> CrowdZoneSummaryOut:
    return CrowdZoneSummaryOut(
        zone_id=zone.id,
        zone_slug=zone.slug,
        zone_name=zone.name,
        zone_type=zone.zone_type,
        latest_reading=CrowdReadingOut.model_validate(reading) if reading else None,
        prototype_notice=CROWD_NOTICE,
    )


@router.get(
    "/zones",
    response_model=ListEnvelope[CrowdZoneSummaryOut],
    summary="Latest crowd density band per zone",
    description=(
        "**Demo prototype.** Every reading is an operator-entered observation "
        "recorded through the admin endpoint below - never a live CCTV, "
        "sensor or headcount feed. Density is an aggregate zone-level band "
        "(green/yellow/orange/red); no individual is tracked or counted "
        "(PRD section 26). A zone with no reading yet returns "
        "`latest_reading: null` rather than a fabricated value."
    ),
)
def list_crowd_zones(db: DbSession) -> ListEnvelope[CrowdZoneSummaryOut]:
    zones, latest_by_zone = list_zone_summaries(db)
    items = [_summary_out(zone, latest_by_zone.get(zone.id)) for zone in zones]
    timestamps = [reading.recorded_at for reading in latest_by_zone.values()]
    return ListEnvelope[CrowdZoneSummaryOut](
        items=items,
        total=len(items),
        last_updated=max(timestamps) if timestamps else None,
    )


@router.get(
    "/zones/{zone_ref}",
    response_model=CrowdZoneDetailOut,
    summary="Latest crowd density band and recent history for one zone",
    description=(
        "Accepts either the numeric zone id or its slug. Returns the latest "
        f"reading plus up to {DEFAULT_HISTORY_LIMIT} of the most recent prior "
        "observations, newest first."
    ),
    responses={404: {"description": "No zone with that id or slug."}},
)
def get_crowd_zone(zone_ref: str, db: DbSession) -> CrowdZoneDetailOut:
    result = get_zone_with_history(db, zone_ref)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found"
        )
    zone, latest, history = result
    return CrowdZoneDetailOut(
        zone_id=zone.id,
        zone_slug=zone.slug,
        zone_name=zone.name,
        zone_type=zone.zone_type,
        latest_reading=CrowdReadingOut.model_validate(latest) if latest else None,
        history=[CrowdReadingOut.model_validate(row) for row in history],
        prototype_notice=CROWD_NOTICE,
    )


@router.post(
    "/zones/{zone_ref}/readings",
    response_model=CrowdReadingCreatedOut,
    status_code=status.HTTP_201_CREATED,
    summary="Record a new crowd density observation for a zone (admin only)",
    description=(
        "**Demo prototype, admin only.** Writes an operator-entered "
        "observation to this project's own database. This endpoint does not "
        "read from, or connect to, any live CCTV, sensor or headcount system "
        "- the authenticated admin calling it is the source of the figure, "
        "exactly as PRD section 26 requires for crowd data that is never "
        "based on biometric identification."
    ),
    responses={
        401: {"description": "Missing, malformed or expired bearer token."},
        403: {"description": "Authenticated, but this role has no admin access."},
        404: {"description": "No zone with that id or slug."},
    },
)
def create_crowd_reading(
    zone_ref: str,
    payload: CrowdReadingCreate,
    db: DbSession,
    admin_user: AdminUser,
) -> CrowdReadingCreatedOut:
    zone = resolve_zone(db, zone_ref)
    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found"
        )
    reading = record_reading(db, zone, payload, admin_user)
    return CrowdReadingCreatedOut(
        reading=CrowdReadingOut.model_validate(reading),
        prototype_notice=CROWD_NOTICE,
    )
