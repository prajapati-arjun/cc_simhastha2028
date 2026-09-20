"""Emergency directory and simulated-SOS schemas (PRD section 15, decision D-02)."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import SosSituationCategory
from app.schemas.common import ORMModel, UtcDateTime


class EmergencyServiceOut(ORMModel):
    id: int
    name: str
    category: str
    phone: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    hours: str | None = None
    notes: str | None = None
    data_source: str
    prototype_notice: str
    updated_at: UtcDateTime


class SosCreate(BaseModel):
    """
    Request body for the SIMULATED SOS endpoint.

    `consent_given` must be true. PRD section 15 requires explicit consent and
    section 31 requires purpose limitation for optional location sharing, so
    consent is a hard validation gate rather than a checkbox we record and
    ignore - and the router refuses to persist coordinates without it.
    """

    model_config = ConfigDict(extra="forbid")

    reporter_name: str | None = Field(default=None, max_length=255)
    reporter_phone: str | None = Field(default=None, max_length=64)
    situation_category: SosSituationCategory
    note: str | None = Field(default=None, max_length=2000)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    consent_given: bool

    @field_validator("consent_given")
    @classmethod
    def _require_consent(cls, v: bool) -> bool:
        if v is not True:
            raise ValueError(
                "consent_given must be true to submit an SOS report "
                "(explicit consent is required before any location or contact "
                "detail is stored)"
            )
        return v


class SosCreatedOut(BaseModel):
    """
    Confirmation for a recorded SOS.

    `simulated` is always true and is a first-class field, not prose: a client
    can branch on it, and no response from this endpoint can be mistaken for a
    real dispatch acknowledgement.
    """

    case_reference: str
    status: str
    simulated: bool
    created_at: UtcDateTime
    prototype_notice: str
