"""
Incident management (PRD section 25).

An `Incident` here is a record in this prototype's own database moving
through a status lifecycle by human admin action. Creating a row, or moving
it through app/services/incident_workflow.py's guarded transitions, notifies
nobody and dispatches nothing to any real police, medical, fire or
government dispatch system - exactly the same posture as `SosIncident`
(app/models/emergency.py). `simulated` is stored, not merely rendered, so a
later export of this table cannot be mistaken for a record of real
dispatches.

"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.notices import INCIDENT_NOTICE
from app.db.base_class import Base
from app.models.enums import IncidentCategory, IncidentPriority, IncidentStatus
from app.models.mixins import SoftDeleteMixin, TimestampMixin

#: SLA response-time budget per priority (PRD Table 3), in minutes. A fixed
#: Sprint-scope table, not an editable config row.
SLA_MINUTES_BY_PRIORITY: dict[str, int] = {
    IncidentPriority.P1.value: 15,
    IncidentPriority.P2.value: 30,
    IncidentPriority.P3.value: 60,
    IncidentPriority.P4.value: 120,
}


class Incident(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "incidents"
    __table_args__ = (Index("ix_incidents_status_priority", "status", "priority"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    #: Never written directly from a request body - only
    #: app/services/incident_workflow.py's apply_transition() may change this
    #: (see app/api/v1/incidents.py's transition endpoint).
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=IncidentStatus.REPORTED.value, index=True
    )
    #: SLA-breach flag (PRD's "SLA-breach escalation" stage). Monotonic: once
    #: true it stays true - a late incident is still late even after it is
    #: later resolved. Set by app/api/v1/incidents.py's _refresh_escalation,
    #: never client-writable.
    escalated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    zone_id: Mapped[int | None] = mapped_column(
        ForeignKey("zones.id", ondelete="SET NULL"), nullable=True, index=True
    )
    zone = relationship("Zone")

    assigned_department: Mapped[str | None] = mapped_column(String(128), nullable=True)

    sla_due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    #: Nullable: most incidents this sprint are admin-recorded directly, not
    #: filed by an authenticated pilgrim account.
    reported_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    #: The "post-incident report" (PRD section 25's final stage) is captured
    #: here rather than as a separate table - a free-text reviewer note, same
    #: shape as LostFoundCase.admin_notes / MissingPersonCase.admin_notes.
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    #: Stored, not merely rendered - see module docstring.
    simulated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    @property
    def prototype_notice(self) -> str:
        return INCIDENT_NOTICE
