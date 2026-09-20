"""
Parking directory service (PRD section 12, roadmap item 2.3).
"""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import Select
from sqlalchemy.orm import Session

from app.api.v1.helpers import published_rows
from app.core.notices import PARKING_AVAILABILITY_NOTICE
from app.models.enums import ParkingType
from app.models.parking import ParkingFacility
from app.schemas.parking import ParkingAvailabilityOut


def parking_list_query(parking_type: ParkingType | None) -> Select:
    stmt = published_rows(ParkingFacility)
    if parking_type is not None:
        stmt = stmt.where(ParkingFacility.parking_type == parking_type.value)
    return stmt


def get_published_parking_or_404(db: Session, parking_ref: str) -> ParkingFacility:
    """Resolve a published ParkingFacility by numeric id or slug (mirrors ghats)."""
    stmt = published_rows(ParkingFacility)
    if parking_ref.isdigit():
        stmt = stmt.where(ParkingFacility.id == int(parking_ref))
    else:
        stmt = stmt.where(ParkingFacility.slug == parking_ref)

    row = db.execute(stmt).scalar_one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parking facility not found"
        )
    return row


def build_availability(row: ParkingFacility) -> ParkingAvailabilityOut:
    return ParkingAvailabilityOut(
        parking_id=row.id,
        slug=row.slug,
        name=row.name,
        parking_type=row.parking_type,
        capacity=row.capacity,
        current_occupancy=row.current_occupancy,
        occupancy_updated_at=row.occupancy_updated_at,
        data_source=row.data_source,
        prototype_notice=PARKING_AVAILABILITY_NOTICE,
        updated_at=row.updated_at,
    )


__all__ = [
    "PARKING_AVAILABILITY_NOTICE",
    "parking_list_query",
    "get_published_parking_or_404",
    "build_availability",
]
