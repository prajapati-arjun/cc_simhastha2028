"""
Crowd Analytics schemas (PRD section 10, section 26, contract addendum).

`CrowdReadingOut` never carries a headcount field, only a band and an
optional coarse range - see app/models/crowd.py for why.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import CrowdDensityLevel, CrowdEstimatedCountBand, CrowdReadingSource
from app.schemas.common import ORMModel, UtcDateTime


class CrowdReadingCreate(BaseModel):
    """Admin-only request body for POST /crowd/zones/{zone_ref}/readings."""

    model_config = ConfigDict(extra="forbid")

    density_level: CrowdDensityLevel
    estimated_count_band: CrowdEstimatedCountBand | None = None
    source: CrowdReadingSource
    recorded_at: datetime | None = Field(
        default=None,
        description=(
            "Defaults to now (UTC) when omitted. May be set to a past "
            "timestamp for an operator logging an observation after the fact."
        ),
    )


class CrowdReadingOut(ORMModel):
    id: int
    zone_id: int
    density_level: str
    estimated_count_band: str | None = None
    source: str
    recorded_at: UtcDateTime
    recorded_by_user_id: int | None = None
    created_at: UtcDateTime


class CrowdZoneSummaryOut(BaseModel):
    """One row of GET /crowd/zones - the latest reading only, no history."""

    zone_id: int
    zone_slug: str
    zone_name: str
    zone_type: str | None = None
    #: None when no observation has ever been recorded for this zone -
    #: disclosed honestly rather than defaulting to a fabricated band.
    latest_reading: CrowdReadingOut | None = None
    prototype_notice: str


class CrowdZoneDetailOut(BaseModel):
    """GET /crowd/zones/{zone_ref} - latest reading plus recent history."""

    zone_id: int
    zone_slug: str
    zone_name: str
    zone_type: str | None = None
    latest_reading: CrowdReadingOut | None = None
    history: list[CrowdReadingOut] = Field(default_factory=list)
    prototype_notice: str


class CrowdReadingCreatedOut(BaseModel):
    reading: CrowdReadingOut
    prototype_notice: str


__all__ = [
    "CrowdReadingCreate",
    "CrowdReadingOut",
    "CrowdZoneSummaryOut",
    "CrowdZoneDetailOut",
    "CrowdReadingCreatedOut",
]
