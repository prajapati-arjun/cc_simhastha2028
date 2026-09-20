"""
Parking directory (PRD section 12, roadmap item 2.3).
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, event, inspect
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.content import Zone, slug_unique_index
from app.models.enums import ParkingType
from app.models.mixins import (
    PointLocationMixin,
    PublishableMixin,
    SoftDeleteMixin,
    TimestampMixin,
    register_point_geom_sync,
)


def _stamp_occupancy_updated_at(mapper, connection, target: "ParkingFacility") -> None:
    """
    Stamp ``occupancy_updated_at`` only when ``current_occupancy`` itself
    changed (or is being set for the first time), not on every unrelated edit.

    Availability here is operator-entered, never a live sensor or camera feed
    (PRD section 12) - see PARKING_AVAILABILITY_NOTICE in app/services/parking.py.
    The timestamp exists so a pilgrim can judge how stale a headcount is,
    which only means something if it tracks the count itself rather than the
    row's general `updated_at`.
    """
    history = inspect(target).attrs.current_occupancy.history
    if target.occupancy_updated_at is None or history.has_changes():
        target.occupancy_updated_at = datetime.now(timezone.utc)


@register_point_geom_sync
class ParkingFacility(
    Base, TimestampMixin, SoftDeleteMixin, PublishableMixin, PointLocationMixin
):
    """Parking directory entry (PRD section 12): lot, capacity, entry/exit info."""

    __tablename__ = "parking_facilities"
    __table_args__ = (
        slug_unique_index("parking_facilities"),
        Index("ix_parking_facilities_type_status", "parking_type", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parking_type: Mapped[str] = mapped_column(String(32), nullable=False)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    #: Operator-entered headcount, never a live sensor/camera reading.
    current_occupancy: Mapped[int | None] = mapped_column(Integer, nullable=True)
    #: Set only when current_occupancy changes - see the listener below.
    occupancy_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    entry_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    exit_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    shuttle_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    zone_id: Mapped[int | None] = mapped_column(
        ForeignKey("zones.id", ondelete="SET NULL"), nullable=True, index=True
    )
    zone: Mapped[Zone | None] = relationship()


event.listen(ParkingFacility, "before_insert", _stamp_occupancy_updated_at)
event.listen(ParkingFacility, "before_update", _stamp_occupancy_updated_at)


__all__ = ["ParkingType", "ParkingFacility"]
