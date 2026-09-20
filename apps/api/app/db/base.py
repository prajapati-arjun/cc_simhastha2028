"""
Import surface for Alembic autogenerate.

Every model module must be imported here so that `Base.metadata` is fully
populated when `migrations/env.py` reads it.
"""
from app.db.base_class import Base  # noqa: F401
from app.models.audit import AuditLog  # noqa: F401
from app.models.cases import LostFoundCase, MissingPersonCase  # noqa: F401
from app.models.content import Announcement, Event, Ghat, Temple, Zone  # noqa: F401
from app.models.emergency import EmergencyService, SosIncident  # noqa: F401
from app.models.user import Role, User  # noqa: F401

__all__ = [
    "Base",
    "AuditLog",
    "LostFoundCase",
    "MissingPersonCase",
    "Announcement",
    "Event",
    "Ghat",
    "Temple",
    "Zone",
    "EmergencyService",
    "SosIncident",
    "Role",
    "User",
]
