"""
Lost & Found and Missing Person case records (PRD section 16, decision D-01).

Privacy posture for this module:
  * The only public read key is case_reference, a cryptographically random
    opaque token. It is NOT derived from `id` and is NOT sequential.
  * There is no public list endpoint and no lookup by name or phone for either
    table. The personal columns below are readable only through an
    authenticated /api/v1/admin/* route, which is the legitimate verification
    purpose (PRD section 31: purpose limitation).
  * GET /api/v1/missing-person/{case_reference} deliberately projects status
    and timestamps only - see app/schemas/cases.py.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.enums import LostFoundStatus, MissingPersonStatus
from app.models.mixins import PointLocationMixin, TimestampMixin, register_point_geom_sync


@register_point_geom_sync
class LostFoundCase(Base, TimestampMixin, PointLocationMixin):
    __tablename__ = "lost_found_cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_reference: Mapped[str] = mapped_column(
        String(32), nullable=False, unique=True, index=True
    )
    report_type: Mapped[str] = mapped_column(String(16), nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # --- personal data: admin-only, never returned by a public route ---
    reporter_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reporter_phone: Mapped[str] = mapped_column(String(64), nullable=False)

    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=LostFoundStatus.SUBMITTED.value, index=True
    )
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)


@register_point_geom_sync
class MissingPersonCase(Base, TimestampMixin, PointLocationMixin):
    __tablename__ = "missing_person_cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_reference: Mapped[str] = mapped_column(
        String(32), nullable=False, unique=True, index=True
    )

    # --- personal data: admin-only. NONE of these fields may appear in the
    # --- public read schema. See tests/test_missing_person_privacy.py.
    person_name: Mapped[str] = mapped_column(String(255), nullable=False)
    person_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    person_gender: Mapped[str | None] = mapped_column(String(32), nullable=True)
    physical_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_seen_location_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    reporter_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reporter_phone: Mapped[str] = mapped_column(String(64), nullable=False)
    reporter_relationship: Mapped[str | None] = mapped_column(String(64), nullable=True)
    consent_given: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=MissingPersonStatus.SUBMITTED.value, index=True
    )
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
