"""Accommodation & essential services schemas (PRD section 17, roadmap item 2.5)."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.models.accommodation import (
    AccommodationPriceTier,
    AccommodationType,
    EssentialServiceCategory,
)
from app.models.enums import ContentStatus
from app.schemas.common import ORMModel, UtcDateTime
from app.schemas.content import OptionalSlug, Slug


# --------------------------------------------------------------------------
# Accommodation
# --------------------------------------------------------------------------
class AccommodationOut(ORMModel):
    id: int
    slug: str
    name: str
    accommodation_type: AccommodationType
    price_tier: AccommodationPriceTier | None = None
    address: str | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    zone_id: int | None = None
    #: PRD section 17: must be visibly distinguishable from a third-party or
    #: commercial listing. Every seeded row is False - see the model docstring.
    verified: bool
    status: str
    data_source: str
    updated_at: UtcDateTime


class AccommodationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: Slug
    name: str = Field(min_length=1, max_length=255)
    accommodation_type: AccommodationType
    price_tier: AccommodationPriceTier | None = None
    address: str | None = None
    contact_name: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=64)
    description: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    zone_id: int | None = None


class AccommodationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: OptionalSlug = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    accommodation_type: AccommodationType | None = None
    price_tier: AccommodationPriceTier | None = None
    address: str | None = None
    contact_name: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=64)
    description: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    zone_id: int | None = None
    status: ContentStatus | None = None
    #: Only a super_admin may flip this - enforced in the admin router,
    #: mirroring Temple.verified.
    verified: bool | None = None


# --------------------------------------------------------------------------
# Essential services
# --------------------------------------------------------------------------
class EssentialServiceOut(ORMModel):
    id: int
    slug: str
    name: str
    category: EssentialServiceCategory
    notes: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    zone_id: int | None = None
    verified: bool
    status: str
    data_source: str
    updated_at: UtcDateTime


class EssentialServiceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: Slug
    name: str = Field(min_length=1, max_length=255)
    category: EssentialServiceCategory
    notes: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    zone_id: int | None = None


class EssentialServiceUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: OptionalSlug = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    category: EssentialServiceCategory | None = None
    notes: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    zone_id: int | None = None
    status: ContentStatus | None = None
    verified: bool | None = None


__all__ = [
    "AccommodationOut",
    "AccommodationCreate",
    "AccommodationUpdate",
    "EssentialServiceOut",
    "EssentialServiceCreate",
    "EssentialServiceUpdate",
]
