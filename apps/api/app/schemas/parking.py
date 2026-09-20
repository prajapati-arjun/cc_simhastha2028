"""Parking directory schemas (PRD section 12, roadmap item 2.3)."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ContentStatus
from app.models.parking import ParkingType
from app.schemas.common import ORMModel, OptionalUtcDateTime, UtcDateTime
from app.schemas.content import OptionalSlug, Slug


class ParkingOut(ORMModel):
    id: int
    slug: str
    name: str
    parking_type: ParkingType
    capacity: int | None = None
    current_occupancy: int | None = None
    occupancy_updated_at: OptionalUtcDateTime = None
    entry_info: str | None = None
    exit_info: str | None = None
    shuttle_note: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    zone_id: int | None = None
    status: str
    data_source: str
    updated_at: UtcDateTime


class ParkingAvailabilityOut(BaseModel):
    """
    Response for GET /api/v1/parking/{id}/availability (roadmap item 2.3).

    `current_occupancy`/`occupancy_updated_at` are operator-entered, never a
    live sensor or camera reading - `prototype_notice` says so in-band and
    both fields stay null until an admin has actually entered a count, rather
    than defaulting to 0 (an empty lot and an un-entered count must not look
    the same).
    """

    parking_id: int
    slug: str
    name: str
    parking_type: ParkingType
    capacity: int | None = None
    current_occupancy: int | None = None
    occupancy_updated_at: OptionalUtcDateTime = None
    data_source: str
    prototype_notice: str
    updated_at: UtcDateTime


class ParkingCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: Slug
    name: str = Field(min_length=1, max_length=255)
    parking_type: ParkingType
    capacity: int | None = Field(default=None, ge=0)
    current_occupancy: int | None = Field(default=None, ge=0)
    entry_info: str | None = None
    exit_info: str | None = None
    shuttle_note: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    zone_id: int | None = None


class ParkingUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: OptionalSlug = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    parking_type: ParkingType | None = None
    capacity: int | None = Field(default=None, ge=0)
    #: The operator-entered occupancy count. Admin PATCH is the only write
    #: path - see ParkingFacility's before_update listener, which stamps
    #: occupancy_updated_at whenever this field actually changes.
    current_occupancy: int | None = Field(default=None, ge=0)
    entry_info: str | None = None
    exit_info: str | None = None
    shuttle_note: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    zone_id: int | None = None
    status: ContentStatus | None = None


__all__ = [
    "ParkingOut",
    "ParkingAvailabilityOut",
    "ParkingCreate",
    "ParkingUpdate",
]
