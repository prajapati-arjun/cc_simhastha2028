"""Response and admin-input schemas for CMS-managed content."""
from __future__ import annotations

import re
from datetime import datetime

from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_validator

from app.models.enums import (
    AnnouncementPriority,
    ContentStatus,
    DataSource,
    EventCategory,
    GhatStatus,
)
from app.schemas.common import ORMModel, OptionalUtcDateTime, UtcDateTime

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _validate_slug(value: str) -> str:
    """Decision D-04: lowercase kebab-case, numerals preserved, Latin only."""
    value = value.strip().lower()
    if not SLUG_PATTERN.match(value):
        raise ValueError(
            "slug must be lowercase kebab-case (letters, digits, single hyphens), "
            "e.g. 'kal-bhairav' or '84-mahadev'"
        )
    return value


def _validate_optional_slug(value: str | None) -> str | None:
    return None if value is None else _validate_slug(value)


#: Slug types carrying decision D-04's format rule, so every create/update
#: schema enforces it identically instead of re-declaring a validator.
Slug = Annotated[str, AfterValidator(_validate_slug)]
OptionalSlug = Annotated[str | None, AfterValidator(_validate_optional_slug)]


# --------------------------------------------------------------------------
# Events
# --------------------------------------------------------------------------
class EventOut(ORMModel):
    id: int
    slug: str
    title: str
    summary: str | None = None
    description: str | None = None
    category: str
    starts_at: UtcDateTime
    ends_at: OptionalUtcDateTime = None
    venue_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    image_url: str | None = None
    status: str
    data_source: str
    updated_at: UtcDateTime


class EventCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: Slug
    title: str = Field(min_length=1, max_length=255)
    summary: str | None = None
    description: str | None = None
    category: EventCategory
    starts_at: datetime
    ends_at: datetime | None = None
    venue_name: str | None = Field(default=None, max_length=255)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    image_url: str | None = Field(default=None, max_length=512)


    @field_validator("ends_at")
    @classmethod
    def _ends_after_starts(cls, v: datetime | None, info):
        starts = info.data.get("starts_at")
        if v is not None and starts is not None and v < starts:
            raise ValueError("ends_at must not be earlier than starts_at")
        return v


class EventUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: OptionalSlug = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    summary: str | None = None
    description: str | None = None
    category: EventCategory | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    venue_name: str | None = Field(default=None, max_length=255)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    image_url: str | None = Field(default=None, max_length=512)
    status: ContentStatus | None = None



# --------------------------------------------------------------------------
# Temples
# --------------------------------------------------------------------------
class TempleOut(ORMModel):
    id: int
    slug: str
    name: str
    short_description: str | None = None
    significance: str | None = None
    timings: str | None = None
    aarti_schedule: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    transport_info: str | None = None
    accessibility_info: str | None = None
    image_url: str | None = None
    status: str
    verified: bool
    data_source: str
    updated_at: UtcDateTime


class TempleCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: Slug
    name: str = Field(min_length=1, max_length=255)
    short_description: str | None = None
    significance: str | None = None
    timings: str | None = None
    aarti_schedule: str | None = None
    address: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    transport_info: str | None = None
    accessibility_info: str | None = None
    image_url: str | None = Field(default=None, max_length=512)



class TempleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: OptionalSlug = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    short_description: str | None = None
    significance: str | None = None
    timings: str | None = None
    aarti_schedule: str | None = None
    address: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    transport_info: str | None = None
    accessibility_info: str | None = None
    image_url: str | None = Field(default=None, max_length=512)
    status: ContentStatus | None = None
    #: Only a super_admin may flip this - see the admin router.
    verified: bool | None = None



# --------------------------------------------------------------------------
# Ghats
# --------------------------------------------------------------------------
class GhatOut(ORMModel):
    id: int
    slug: str
    name: str
    description: str | None = None
    bathing_info: str | None = None
    facilities: list[str] = Field(default_factory=list)
    accessibility_info: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    image_url: str | None = None
    status: str
    data_source: str
    updated_at: UtcDateTime


class GhatStatusOut(BaseModel):
    """
    Response for GET /api/v1/ghats/{id}/status.

    `crowd_level` is always null this sprint. No crowd sensor, CCTV feed or
    headcount source is connected, and a fabricated green/amber/red badge on a
    bathing-ghat safety surface could influence where someone takes a family
    into a river. The prototype_notice says so in-band.
    """

    ghat_id: int
    slug: str
    name: str
    status: str
    crowd_level: None = None
    advisory: str | None = None
    data_source: str
    prototype_notice: str
    updated_at: UtcDateTime


class GhatCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: Slug
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    bathing_info: str | None = None
    facilities: list[str] = Field(default_factory=list)
    accessibility_info: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    image_url: str | None = Field(default=None, max_length=512)
    operational_status: GhatStatus = GhatStatus.OPEN
    advisory: str | None = None



class GhatUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: OptionalSlug = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    bathing_info: str | None = None
    facilities: list[str] | None = None
    accessibility_info: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    image_url: str | None = Field(default=None, max_length=512)
    operational_status: GhatStatus | None = None
    advisory: str | None = None
    status: ContentStatus | None = None



# --------------------------------------------------------------------------
# Announcements
# --------------------------------------------------------------------------
class AnnouncementOut(ORMModel):
    id: int
    slug: str
    title: str
    body: str
    priority: str
    published_at: OptionalUtcDateTime = None
    expires_at: OptionalUtcDateTime = None
    status: str
    data_source: str
    updated_at: UtcDateTime


class AnnouncementCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: Slug
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)
    priority: AnnouncementPriority = AnnouncementPriority.NORMAL
    published_at: datetime | None = None
    expires_at: datetime | None = None



class AnnouncementUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: OptionalSlug = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    body: str | None = Field(default=None, min_length=1)
    priority: AnnouncementPriority | None = None
    published_at: datetime | None = None
    expires_at: datetime | None = None
    status: ContentStatus | None = None



__all__ = [
    "ContentStatus",
    "DataSource",
    "EventOut",
    "EventCreate",
    "EventUpdate",
    "TempleOut",
    "TempleCreate",
    "TempleUpdate",
    "GhatOut",
    "GhatStatusOut",
    "GhatCreate",
    "GhatUpdate",
    "AnnouncementOut",
    "AnnouncementCreate",
    "AnnouncementUpdate",
]
