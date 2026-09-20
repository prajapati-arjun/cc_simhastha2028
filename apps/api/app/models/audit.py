"""Audit trail (PRD section 16 audit-trail-for-sensitive-cases, section 30)."""
from __future__ import annotations

from typing import Any

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import TimestampMixin


class AuditLog(Base, TimestampMixin):
    """
    Append-only record of every admin write and every safety-critical public
    submission. No public endpoint exposes these rows this sprint.

    `detail` never stores raw personal data - it records which fields changed,
    not the values of name/phone/photo columns (PRD section 31 data
    minimisation). See app/services/audit.py.
    """

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    #: NULL for unauthenticated public submissions (SOS, lost-found, missing-person).
    actor_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    detail: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
