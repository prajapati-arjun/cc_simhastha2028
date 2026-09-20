"""CMS-managed master data: Zone, Temple, Ghat, Event, Announcement."""
from __future__ import annotations

from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import AnnouncementPriority, GhatStatus
from app.models.mixins import (
    PointLocationMixin,
    PublishableMixin,
    SoftDeleteMixin,
    TimestampMixin,
    register_point_geom_sync,
)


def slug_unique_index(table: str) -> Index:
    """
    Slugs (decision D-04) are unique among *live* rows only: a soft-deleted row
    must not permanently burn a slug an editor may legitimately want to reuse.
    """
    return Index(
        f"uq_{table}_slug_active",
        "slug",
        unique=True,
        postgresql_where=text("deleted_at IS NULL"),
    )


@register_point_geom_sync
class Zone(Base, TimestampMixin, SoftDeleteMixin, PointLocationMixin):
    """
    Operational zone master data (PRD section 36). Schema-only this sprint —
    there is deliberately no public zone API, because crowd/traffic readings
    are out of scope and an empty zone feed would read as a broken live layer.
    """

    __tablename__ = "zones"
    __table_args__ = (
        slug_unique_index("zones"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    zone_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    #: Genuine PostGIS territory: a zone boundary has no scalar equivalent.
    boundary = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326, spatial_index=True), nullable=True
    )


@register_point_geom_sync
class Temple(Base, TimestampMixin, SoftDeleteMixin, PublishableMixin, PointLocationMixin):
    """Temple / spiritual destination (PRD section 13)."""

    __tablename__ = "temples"
    __table_args__ = (
        slug_unique_index("temples"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    short_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    significance: Mapped[str | None] = mapped_column(Text, nullable=True)
    timings: Mapped[str | None] = mapped_column(Text, nullable=True)
    aarti_schedule: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    transport_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    accessibility_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    #: True only when a named authority has signed the record off. Nothing in
    #: this prototype is authority-verified, so every seeded row is False.
    verified: Mapped[bool] = mapped_column(nullable=False, default=False)

    zone_id: Mapped[int | None] = mapped_column(
        ForeignKey("zones.id", ondelete="SET NULL"), nullable=True, index=True
    )
    zone: Mapped[Zone | None] = relationship()


@register_point_geom_sync
class Ghat(Base, TimestampMixin, SoftDeleteMixin, PublishableMixin, PointLocationMixin):
    """Bathing ghat (PRD section 9/13, decision D-03)."""

    __tablename__ = "ghats"
    __table_args__ = (
        slug_unique_index("ghats"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    bathing_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    facilities: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    accessibility_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    #: Operational state surfaced by GET /api/v1/ghats/{id}/status.
    operational_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=GhatStatus.OPEN.value
    )
    advisory: Mapped[str | None] = mapped_column(Text, nullable=True)
    #: Intentionally always NULL this sprint. No crowd sensor, CCTV or
    #: headcount source exists, and inventing a green/amber/red value on a
    #: safety surface would be a lie the map would render as fact.
    crowd_level: Mapped[str | None] = mapped_column(String(32), nullable=True)

    zone_id: Mapped[int | None] = mapped_column(
        ForeignKey("zones.id", ondelete="SET NULL"), nullable=True, index=True
    )
    zone: Mapped[Zone | None] = relationship()


@register_point_geom_sync
class Event(Base, TimestampMixin, SoftDeleteMixin, PublishableMixin, PointLocationMixin):
    """Simhastha calendar event (PRD section 8)."""

    __tablename__ = "events"
    __table_args__ = (
        slug_unique_index("events"),
        Index("ix_events_starts_at_status", "starts_at", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    venue_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)


class Announcement(Base, TimestampMixin, SoftDeleteMixin, PublishableMixin):
    """Public announcement / alert (PRD section 28)."""

    __tablename__ = "announcements"
    __table_args__ = (
        slug_unique_index("announcements"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(
        String(32), nullable=False, default=AnnouncementPriority.NORMAL.value, index=True
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
