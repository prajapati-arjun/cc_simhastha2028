"""
Command Center schemas (PRD section 24).

The response is split into three sections that must stay visually distinct on
any screen that renders it:

  1. ``observed``        - real rows read from this project's own database.
  2. ``recommendations``  - model-generated suggestions. None exist in this
                            prototype; the section is present but always
                            empty, never a simulated recommendation engine.
  3. ``human_decisions``  - state that an authenticated admin set explicitly
                            (e.g. a case's current status), not inferred or
                            generated.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import OptionalUtcDateTime, UtcDateTime
from app.schemas.crowd import CrowdReadingOut


class CommandCenterZoneOut(BaseModel):
    zone_id: int
    zone_slug: str
    zone_name: str
    zone_type: str | None = None
    #: None when no observation has ever been recorded for this zone.
    latest_crowd_reading: CrowdReadingOut | None = None


class CommandCenterCriticalAlertOut(BaseModel):
    id: int
    slug: str
    title: str
    body: str
    priority: str
    published_at: OptionalUtcDateTime = None
    expires_at: OptionalUtcDateTime = None


class CommandCenterCaseTotalsOut(BaseModel):
    """
    Platform-wide, not per zone.

    SosIncident, LostFoundCase and MissingPersonCase (app/models/emergency.py,
    app/models/cases.py - neither module is edited here) carry only an
    optional latitude/longitude, no zone_id. Zone.boundary is unpopulated in
    this sprint's seed data. Attributing a case to a zone would therefore mean
    fabricating a spatial match this data cannot honestly support, so these
    are reported as simple totals - see `case_totals_note`.
    """

    open_sos_incidents: int
    open_lost_found_cases: int
    open_missing_person_cases: int


class CommandCenterObservedOut(BaseModel):
    """Section 1: observed data."""

    zones: list[CommandCenterZoneOut] = Field(default_factory=list)
    case_totals: CommandCenterCaseTotalsOut
    case_totals_note: str
    critical_announcements: list[CommandCenterCriticalAlertOut] = Field(
        default_factory=list
    )


class CommandCenterRecommendationsOut(BaseModel):
    """Section 2: model-generated recommendations - deliberately empty."""

    available: bool = False
    items: list[str] = Field(default_factory=list)
    note: str


class CommandCenterDecisionOut(BaseModel):
    """
    One human decision: an admin-set status on a case record.

    Never carries a person's name, phone, description or precise location -
    only the case_reference (an opaque token; see app/models/cases.py) and
    its status, matching the privacy posture of the public case-lookup
    endpoints.
    """

    entity_type: str
    case_reference: str
    status: str
    updated_at: UtcDateTime


class CommandCenterHumanDecisionsOut(BaseModel):
    """Section 3: human decisions."""

    note: str
    recent_status_decisions: list[CommandCenterDecisionOut] = Field(
        default_factory=list
    )


class CommandCenterOverviewOut(BaseModel):
    generated_at: UtcDateTime
    prototype_notice: str
    observed: CommandCenterObservedOut
    recommendations: CommandCenterRecommendationsOut
    human_decisions: CommandCenterHumanDecisionsOut


__all__ = [
    "CommandCenterZoneOut",
    "CommandCenterCriticalAlertOut",
    "CommandCenterCaseTotalsOut",
    "CommandCenterObservedOut",
    "CommandCenterRecommendationsOut",
    "CommandCenterDecisionOut",
    "CommandCenterHumanDecisionsOut",
    "CommandCenterOverviewOut",
]
