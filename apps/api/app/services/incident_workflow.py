"""
Incident lifecycle state machine (PRD section 25).

Mirrors app/services/workflow.py's CONTENT_TRANSITIONS / apply_transition
pattern rather than inventing a new style: `status` is never a free-form
column write, and only `apply_transition()` (re-exported from workflow.py
below) may produce a new one. An incident here is a record in this
prototype's own database moving through this lifecycle by human admin
action - creating or transitioning a row does not notify or dispatch anyone
real (see INCIDENT_NOTICE in app/models/incident.py).

PRD section 25's stages map onto `Incident.status` plus two things that are
deliberately NOT statuses of their own:

  * priority / assigned_department / zone_id are attributes set alongside a
    transition, not stages in the state machine - "priority assignment" and
    "department/zone assignment" both happen on the reported -> classified
    and classified -> assigned moves respectively (or via a later PATCH),
    not via a separate status value each.
  * `escalated` is an orthogonal boolean (PRD's "SLA-breach escalation"),
    not a status: a P1 incident stuck in `in_response` past its SLA is still
    `in_response`, just late. Folding escalation into status would force a
    branch per stage ("classified-and-late", "assigned-and-late", ...) for
    what is really "on time" vs "late" layered on top of the existing stage.
  * "post-incident report" is the `admin_notes` text captured on the final
    `resolved` -> `closed` move, not a seventh status.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.models.incident import SLA_MINUTES_BY_PRIORITY, IncidentPriority, IncidentStatus
from app.services.workflow import InvalidTransition, apply_transition

#: reported -> classified -> assigned -> in_response -> resolved -> closed.
#: Terminal at `closed`; reopening a closed incident is a new incident, not a
#: status write - same reasoning as MISSING_PERSON_TRANSITIONS' terminal
#: resolved/closed states in app/services/workflow.py.
INCIDENT_TRANSITIONS: dict[str, set[str]] = {
    IncidentStatus.REPORTED.value: {IncidentStatus.CLASSIFIED.value},
    IncidentStatus.CLASSIFIED.value: {IncidentStatus.ASSIGNED.value},
    IncidentStatus.ASSIGNED.value: {IncidentStatus.IN_RESPONSE.value},
    IncidentStatus.IN_RESPONSE.value: {IncidentStatus.RESOLVED.value},
    IncidentStatus.RESOLVED.value: {IncidentStatus.CLOSED.value},
    IncidentStatus.CLOSED.value: set(),
}


def sla_due_at_for(priority: str, from_time: datetime | None = None) -> datetime:
    """SLA due time for a priority, per PRD Table 3's response-time budget."""
    base = from_time or datetime.now(timezone.utc)
    minutes = SLA_MINUTES_BY_PRIORITY.get(
        IncidentPriority(priority).value, SLA_MINUTES_BY_PRIORITY[IncidentPriority.P4.value]
    )
    return base + timedelta(minutes=minutes)


def is_breached(sla_due_at: datetime | None, status: str, *, now: datetime | None = None) -> bool:
    """
    True when an incident has passed its SLA due time without resolving.

    Resolved/closed incidents cannot be "breached" retroactively by the mere
    passage of time after the fact - escalation only ever describes an
    incident still in flight.
    """
    if sla_due_at is None:
        return False
    if status in (IncidentStatus.RESOLVED.value, IncidentStatus.CLOSED.value):
        return False
    moment = now or datetime.now(timezone.utc)
    if sla_due_at.tzinfo is None:
        sla_due_at = sla_due_at.replace(tzinfo=timezone.utc)
    return moment > sla_due_at


__all__ = [
    "InvalidTransition",
    "apply_transition",
    "INCIDENT_TRANSITIONS",
    "sla_due_at_for",
    "is_breached",
]
