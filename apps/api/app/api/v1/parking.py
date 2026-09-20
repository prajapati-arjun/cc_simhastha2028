"""Public Parking API (PRD section 12, roadmap item 2.3)."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.v1.helpers import LimitQuery, OffsetQuery, count_of
from app.core.deps import DbSession
from app.models.parking import ParkingFacility, ParkingType
from app.schemas.common import ListEnvelope, build_envelope
from app.schemas.parking import ParkingAvailabilityOut, ParkingOut
from app.services.parking import (
    build_availability,
    get_published_parking_or_404,
    parking_list_query,
)

router = APIRouter(prefix="/parking", tags=["parking"])


@router.get(
    "",
    response_model=ListEnvelope[ParkingOut],
    summary="List published parking facilities",
    description=(
        "`current_occupancy`/`occupancy_updated_at` are operator-entered "
        "placeholder data, not a live sensor feed - see the availability "
        "sub-resource for the full disclosure."
    ),
)
def list_parking(
    db: DbSession,
    parking_type: ParkingType | None = Query(
        default=None, description="Filter by parking type."
    ),
    limit: int = LimitQuery,
    offset: int = OffsetQuery,
) -> ListEnvelope[ParkingOut]:
    stmt = parking_list_query(parking_type)
    total = count_of(db, stmt)
    rows = (
        db.execute(stmt.order_by(ParkingFacility.id.asc()).limit(limit).offset(offset))
        .scalars()
        .all()
    )
    return ListEnvelope[ParkingOut].model_validate(
        build_envelope(rows, [ParkingOut.model_validate(row) for row in rows], total)
    )


@router.get(
    "/{parking_ref}",
    response_model=ParkingOut,
    summary="Get one published parking facility",
    description="Accepts either the numeric id or the slug.",
    responses={404: {"description": "No published parking facility with that id or slug."}},
)
def get_parking(parking_ref: str, db: DbSession) -> ParkingOut:
    return ParkingOut.model_validate(get_published_parking_or_404(db, parking_ref))


@router.get(
    "/{parking_ref}/availability",
    response_model=ParkingAvailabilityOut,
    summary="Get operator-entered occupancy for one parking facility",
    description=(
        "**Operator-entered placeholder data.** No live sensor, camera or "
        "gate-counter feed is connected in this prototype - see "
        "`prototype_notice` on the response. Matches roadmap item 2.3's "
        "`GET /api/v1/parking/{id}/availability`."
    ),
    responses={404: {"description": "No published parking facility with that id or slug."}},
)
def get_parking_availability(parking_ref: str, db: DbSession) -> ParkingAvailabilityOut:
    row = get_published_parking_or_404(db, parking_ref)
    return build_availability(row)
