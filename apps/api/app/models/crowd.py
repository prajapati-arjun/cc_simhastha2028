"""
Crowd Analytics (PRD section 10, section 26).

Hard constraints, encoded here so they cannot be bypassed by a later caller:

  * Every reading is an aggregate, zone-level density BAND
    (green/yellow/orange/red). There is deliberately no per-person count, no
    headcount column and no path from this table to an individual - PRD
    section 26 requires no biometrics and no facial recognition, ever, and
    PRD section 10 explicitly does not require individual-level tracking for
    basic crowd density.
  * `source` never names a live sensor, CCTV feed or dispatch system - only
    an admin/operator action ever writes a row here (see CrowdReadingSource
    below and app/services/crowd.py).
  * `estimated_count_band` is a coarse range for operational planning, not an
    exact figure - it is one of a small fixed set of bands, never a number.

"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.content import Zone
from app.models.enums import CrowdReadingSource
from app.models.mixins import TimestampMixin


class CrowdReading(Base, TimestampMixin):
    """
    A single operator-entered crowd density observation for one zone.

    Rows are append-only observations, not editable CMS content, so there is
    no SoftDeleteMixin/PublishableMixin here - closer in spirit to
    SosIncident (app/models/emergency.py) than to Temple/Ghat.
    """

    __tablename__ = "crowd_readings"
    __table_args__ = (
        Index("ix_crowd_readings_zone_recorded", "zone_id", "recorded_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    zone_id: Mapped[int] = mapped_column(
        ForeignKey("zones.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    zone: Mapped[Zone] = relationship()

    density_level: Mapped[str] = mapped_column(String(32), nullable=False)
    #: Nullable: an operator may report a band without attempting a count.
    estimated_count_band: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source: Mapped[str] = mapped_column(
        String(32), nullable=False, default=CrowdReadingSource.OPERATOR_ENTERED.value
    )

    #: When the observation was made - may be backdated by an operator logging
    #: after the fact. Distinct from TimestampMixin.created_at (when the row
    #: was written).
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    recorded_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
