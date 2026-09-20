"""
Pilgrimage Planner schemas (PRD section 7, Sprint 2, contract section 10).

No personal data is collected here (no reporter name/phone/consent) - a
planning preference is not a case record, so this module deliberately does
not follow the cases.py privacy pattern. Nothing this endpoint accepts or
returns is persisted; see app/services/planner.py.
"""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import (
    AccessibilityRequirement,
    AccommodationPreference,
    AgeGroup,
    PilgrimInterest,
    TransportMode,
)
from app.schemas.common import UtcDateTime

#: Bounds the generated response size and rules out a request that could not
#: describe a real Simhastha visit.
MAX_TRIP_DAYS = 30


class PlannerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    arrival_date: date
    departure_date: date
    party_size: int = Field(ge=1, le=200)
    age_groups: list[AgeGroup] = Field(default_factory=list)
    transport_mode: TransportMode
    accommodation_preference: AccommodationPreference
    interests: list[PilgrimInterest] = Field(default_factory=list)
    accessibility_requirements: list[AccessibilityRequirement] = Field(
        default_factory=list
    )

    @field_validator("departure_date")
    @classmethod
    def _validate_trip_range(cls, v: date, info):
        arrival = info.data.get("arrival_date")
        if arrival is None:
            return v
        if v < arrival:
            raise ValueError("departure_date must not be earlier than arrival_date")
        if (v - arrival).days + 1 > MAX_TRIP_DAYS:
            raise ValueError(f"trip length must not exceed {MAX_TRIP_DAYS} days")
        return v


class PlannerTempleOut(BaseModel):
    id: int
    slug: str
    name: str
    short_description: str | None = None


class PlannerGhatOut(BaseModel):
    id: int
    slug: str
    name: str


class PlannerEventOut(BaseModel):
    id: int
    slug: str
    title: str
    category: str
    starts_at: UtcDateTime
    venue_name: str | None = None


class PlannerDayOut(BaseModel):
    date: date
    day_number: int
    temples: list[PlannerTempleOut] = Field(default_factory=list)
    ghats: list[PlannerGhatOut] = Field(default_factory=list)
    events: list[PlannerEventOut] = Field(default_factory=list)
    #: True when no temple, ghat or event was assigned this day - an honest
    #: "nothing scheduled" flag rather than a silently empty day.
    rest_period: bool


class PlannerResponse(BaseModel):
    arrival_date: date
    departure_date: date
    party_size: int
    age_groups: list[str]
    transport_mode: str
    accommodation_preference: str
    interests: list[str]
    accessibility_requirements: list[str]
    days: list[PlannerDayOut]
    #: Temples/ghats that did not fit within the trip length at the per-day
    #: cap. Disclosed rather than silently dropped.
    unscheduled_temples: list[PlannerTempleOut] = Field(default_factory=list)
    unscheduled_ghats: list[PlannerGhatOut] = Field(default_factory=list)
    transport_note: str
    accommodation_note: str
    accessibility_note: str | None = None
    interest_note: str | None = None
    data_source: str
    prototype_notice: str
    generated_at: UtcDateTime


__all__ = [
    "MAX_TRIP_DAYS",
    "PlannerRequest",
    "PlannerTempleOut",
    "PlannerGhatOut",
    "PlannerEventOut",
    "PlannerDayOut",
    "PlannerResponse",
]
