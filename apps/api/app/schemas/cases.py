"""
Lost & Found and Missing Person schemas (PRD section 16, decision D-01).

THE CRITICAL RULE IN THIS FILE: `MissingPersonPublicOut` carries status and
timestamps only. It must never gain `person_name`, `person_age`,
`person_gender`, `physical_description`, `photo_url`, `last_seen_location_text`,
`latitude`, `longitude`, or any `reporter_*` field. The only way to read a case
back is an opaque, cryptographically random `case_reference`; there is no list
endpoint and no lookup by name or phone. Full detail is reachable solely
through an authenticated /api/v1/admin/* route, which is the legitimate
verification purpose.

tests/test_missing_person_privacy.py asserts this directly against the model's
declared field set, so adding a personal field here fails the suite.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import LostFoundCategory, LostFoundReportType
from app.schemas.common import ORMModel, OptionalUtcDateTime, UtcDateTime

#: Mobile handset clocks drift. Rejecting a timestamp two seconds ahead of the
#: server would fail a genuine report for no safety benefit, so "not in the
#: future" is enforced with a small, explicit skew allowance.
CLOCK_SKEW_TOLERANCE = timedelta(minutes=2)


def _reject_future(value: datetime | None, field_name: str) -> datetime | None:
    if value is None:
        return None
    moment = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if moment > datetime.now(timezone.utc) + CLOCK_SKEW_TOLERANCE:
        raise ValueError(f"{field_name} must not be in the future")
    return value


def _require_non_empty_phone(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("reporter_phone is required and must not be blank")
    return stripped


# --------------------------------------------------------------------------
# Lost & Found
# --------------------------------------------------------------------------
class LostFoundCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report_type: LostFoundReportType
    category: LostFoundCategory
    description: str = Field(min_length=10, max_length=2000)
    location_text: str | None = Field(default=None, max_length=1000)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    occurred_at: datetime | None = None
    reporter_name: str | None = Field(default=None, max_length=255)
    reporter_phone: str = Field(min_length=1, max_length=64)
    image_url: str | None = Field(default=None, max_length=512)

    @field_validator("occurred_at")
    @classmethod
    def _occurred_not_future(cls, v: datetime | None) -> datetime | None:
        return _reject_future(v, "occurred_at")

    @field_validator("reporter_phone")
    @classmethod
    def _phone_non_empty(cls, v: str) -> str:
        return _require_non_empty_phone(v)


class CaseCreatedOut(BaseModel):
    """Shared POST confirmation for both case types."""

    case_reference: str
    status: str
    created_at: UtcDateTime
    prototype_notice: str


class LostFoundPublicOut(BaseModel):
    """
    Public read for GET /api/v1/lost-found/{case_reference}.

    Returns the non-identifying descriptors the reporter already knows (they
    typed them) plus progress. It deliberately omits reporter_name,
    reporter_phone, the free-text description, the image and the coordinates,
    so a leaked or brute-forced reference still discloses almost nothing.
    """

    case_reference: str
    report_type: str
    category: str
    status: str
    created_at: UtcDateTime
    updated_at: UtcDateTime
    prototype_notice: str


# --------------------------------------------------------------------------
# Missing Person
# --------------------------------------------------------------------------
class MissingPersonCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    person_name: str = Field(min_length=1, max_length=255)
    person_age: int | None = Field(default=None, ge=0, le=120)
    person_gender: str | None = Field(default=None, max_length=32)
    physical_description: str | None = Field(default=None, max_length=2000)
    last_seen_location_text: str | None = Field(default=None, max_length=1000)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    last_seen_at: datetime | None = None
    photo_url: str | None = Field(default=None, max_length=512)
    reporter_name: str | None = Field(default=None, max_length=255)
    reporter_phone: str = Field(min_length=1, max_length=64)
    reporter_relationship: str | None = Field(default=None, max_length=64)
    consent_given: bool

    @field_validator("last_seen_at")
    @classmethod
    def _last_seen_not_future(cls, v: datetime | None) -> datetime | None:
        return _reject_future(v, "last_seen_at")

    @field_validator("reporter_phone")
    @classmethod
    def _phone_non_empty(cls, v: str) -> str:
        return _require_non_empty_phone(v)

    @field_validator("consent_given")
    @classmethod
    def _require_consent(cls, v: bool) -> bool:
        if v is not True:
            raise ValueError(
                "consent_given must be true to submit a missing-person report"
            )
        return v


class MissingPersonPublicOut(BaseModel):
    """
    Public read for GET /api/v1/missing-person/{case_reference}.

    STATUS AND TIMESTAMPS ONLY. Do not add fields to this model. See the module
    docstring - a personal field here would turn a reference-holder (or anyone
    who guessed one) into a reader of a child's name, photo and last known
    location at an event serving millions of people.
    """

    case_reference: str
    status: str
    created_at: UtcDateTime
    updated_at: UtcDateTime
    prototype_notice: str


# --------------------------------------------------------------------------
# Admin-only views (authenticated verification queue)
# --------------------------------------------------------------------------
class LostFoundAdminOut(ORMModel):
    """Full case detail. Reachable only with an admin bearer token."""

    id: int
    case_reference: str
    report_type: str
    category: str
    description: str
    location_text: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    occurred_at: OptionalUtcDateTime = None
    image_url: str | None = None
    reporter_name: str | None = None
    reporter_phone: str
    status: str
    admin_notes: str | None = None
    created_at: UtcDateTime
    updated_at: UtcDateTime


class MissingPersonAdminOut(ORMModel):
    """Full case detail. Reachable only with an admin bearer token."""

    id: int
    case_reference: str
    person_name: str
    person_age: int | None = None
    person_gender: str | None = None
    physical_description: str | None = None
    last_seen_location_text: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    last_seen_at: OptionalUtcDateTime = None
    photo_url: str | None = None
    reporter_name: str | None = None
    reporter_phone: str
    reporter_relationship: str | None = None
    consent_given: bool
    status: str
    admin_notes: str | None = None
    created_at: UtcDateTime
    updated_at: UtcDateTime


class CaseStatusUpdate(BaseModel):
    """
    Admin PATCH body for both verification queues.

    Status is the only mutable field: an admin moves a case through the
    workflow and annotates it, but cannot rewrite what the reporter submitted.
    """

    model_config = ConfigDict(extra="forbid")

    status: str
    admin_notes: str | None = Field(default=None, max_length=2000)
