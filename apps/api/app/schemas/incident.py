"""
Incident management schemas (PRD section 25).

`status` is never accepted as a free-form field on create/update - the only
way to move it is POST /api/v1/incidents/{id}/transition, which runs through
app/services/incident_workflow.py's guarded transition table (the same
"one table, not scattered ifs" contract as CONTENT_TRANSITIONS in
app/services/workflow.py). `escalated`, `sla_due_at` and `resolved_at` are
likewise server-computed and never client-writable.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.models.incident import IncidentCategory, IncidentPriority, IncidentStatus
from app.schemas.common import ORMModel, OptionalUtcDateTime, UtcDateTime


class IncidentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: IncidentCategory
    priority: IncidentPriority = IncidentPriority.P4
    title: str = Field(min_length=3, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    zone_id: int | None = None
    assigned_department: str | None = Field(default=None, max_length=128)
    reported_by_user_id: int | None = None


class IncidentUpdate(BaseModel):
    """
    Every mutable field except `status` (use the transition endpoint) and the
    server-computed `escalated` / `sla_due_at` / `resolved_at` fields.
    """

    model_config = ConfigDict(extra="forbid")

    category: IncidentCategory | None = None
    priority: IncidentPriority | None = None
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    zone_id: int | None = None
    assigned_department: str | None = Field(default=None, max_length=128)
    admin_notes: str | None = Field(default=None, max_length=4000)


class IncidentTransitionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: IncidentStatus


class IncidentOut(ORMModel):
    id: int
    category: str
    priority: str
    status: str
    escalated: bool
    title: str
    description: str | None = None
    zone_id: int | None = None
    assigned_department: str | None = None
    sla_due_at: OptionalUtcDateTime = None
    resolved_at: OptionalUtcDateTime = None
    reported_by_user_id: int | None = None
    admin_notes: str | None = None
    simulated: bool
    created_at: UtcDateTime
    updated_at: UtcDateTime
    prototype_notice: str


__all__ = [
    "IncidentCreate",
    "IncidentUpdate",
    "IncidentTransitionRequest",
    "IncidentOut",
]
