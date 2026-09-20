"""Emergency directory and the SIMULATED SOS incident record (PRD section 15)."""
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import SosSituationCategory
from app.models.mixins import (
    PointLocationMixin,
    PublishableMixin,
    SoftDeleteMixin,
    TimestampMixin,
    register_point_geom_sync,
)


@register_point_geom_sync
class EmergencyService(
    Base, TimestampMixin, SoftDeleteMixin, PublishableMixin, PointLocationMixin
):
    """
    A directory entry for a help point.

    Every seeded row carries a deliberately fake +91-00000-000NN phone number.
    A pilgrim must never be able to tap-to-call a number this prototype implies
    is staffed, so real emergency numbers (100/102/108/112) and real station
    numbers are never seeded here.
    """

    __tablename__ = "emergency_services"
    __table_args__ = (Index("ix_emergency_services_category", "category", "status"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    hours: Mapped[str | None] = mapped_column(String(128), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    zone_id: Mapped[int | None] = mapped_column(
        ForeignKey("zones.id", ondelete="SET NULL"), nullable=True, index=True
    )
    zone = relationship("Zone")

    @property
    def prototype_notice(self) -> str:
        """
        Attached to the model, not the route, so that every serialisation of an
        emergency directory row carries the disclosure. A future endpoint
        cannot emit one of these rows without it.
        """
        from app.core.notices import EMERGENCY_NOTICE

        return EMERGENCY_NOTICE


@register_point_geom_sync
class SosIncident(Base, TimestampMixin, PointLocationMixin):
    """
    A simulated SOS record (decision D-02).

    This table is a test-database sink. Writing a row here dispatches nothing,
    pages nobody, and reaches no police, medical or government system. The
    `simulated` column is stored (not merely rendered) so that any later export
    of this table cannot be mistaken for a record of real dispatches.
    """

    __tablename__ = "sos_incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_reference: Mapped[str] = mapped_column(
        String(32), nullable=False, unique=True, index=True
    )
    situation_category: Mapped[str] = mapped_column(
        String(64), nullable=False, default=SosSituationCategory.OTHER.value
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reporter_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reporter_phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    #: Location is only persisted when consent_given is true (PRD section 31,
    #: explicit consent for optional location sharing).
    consent_given: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="recorded")
    simulated: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
