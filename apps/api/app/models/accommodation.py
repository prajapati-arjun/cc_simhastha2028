"""
Accommodation & essential services directory (PRD section 17, roadmap item 2.5).

Single file, two tables: PRD section 17 groups hotels/dharamshalas/ashrams
/tent camps/government accommodation together with food services, bhandaras,
drinking water, toilets and changing facilities, but they are not the same
kind of record (price tier and booking-adjacent fields make no sense on a
drinking-water point). Two lightweight tables sharing the same mixins is
simpler than one table with a pile of nullable columns that only apply to
half its rows.
"""
from __future__ import annotations

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.content import Zone, slug_unique_index
from app.models.enums import AccommodationPriceTier, AccommodationType, EssentialServiceCategory
from app.models.mixins import (
    PointLocationMixin,
    PublishableMixin,
    SoftDeleteMixin,
    TimestampMixin,
    register_point_geom_sync,
)


@register_point_geom_sync
class Accommodation(
    Base, TimestampMixin, SoftDeleteMixin, PublishableMixin, PointLocationMixin
):
    """Hotel / dharamshala / ashram / tent camp / government stay (PRD section 17)."""

    __tablename__ = "accommodations"
    __table_args__ = (
        slug_unique_index("accommodations"),
        Index("ix_accommodations_type_status", "accommodation_type", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    accommodation_type: Mapped[str] = mapped_column(String(32), nullable=False)
    price_tier: Mapped[str | None] = mapped_column(String(32), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    #: PRD section 17's explicit requirement: listings must visibly distinguish
    #: officially verified entries from third-party/commercial ones. This is
    #: the same stub Temple already carries - every seeded row is False,
    #: because nothing in this prototype has been signed off by an authority.
    verified: Mapped[bool] = mapped_column(nullable=False, default=False)

    zone_id: Mapped[int | None] = mapped_column(
        ForeignKey("zones.id", ondelete="SET NULL"), nullable=True, index=True
    )
    zone: Mapped[Zone | None] = relationship()


@register_point_geom_sync
class EssentialService(
    Base, TimestampMixin, SoftDeleteMixin, PublishableMixin, PointLocationMixin
):
    """Food service / bhandara / drinking water / toilet / changing facility."""

    __tablename__ = "essential_services"
    __table_args__ = (
        slug_unique_index("essential_services"),
        Index("ix_essential_services_category_status", "category", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    #: Same officially-verified-vs-third-party distinction as Accommodation
    #: above (PRD section 17) - a government-run bhandara or water point is
    #: not otherwise distinguishable from a vendor-run one.
    verified: Mapped[bool] = mapped_column(nullable=False, default=False)

    zone_id: Mapped[int | None] = mapped_column(
        ForeignKey("zones.id", ondelete="SET NULL"), nullable=True, index=True
    )
    zone: Mapped[Zone | None] = relationship()


__all__ = [
    "AccommodationType",
    "AccommodationPriceTier",
    "EssentialServiceCategory",
    "Accommodation",
    "EssentialService",
]
