"""
Controlled vocabularies shared by ORM models, Pydantic schemas and the seed
script. Values are frozen by Docs/API_CONTRACT.md — do not rename them without
updating the contract and telling Frontend.

Storage note: these are persisted as VARCHAR rather than native PostgreSQL
ENUM types. Native enums require an ALTER TYPE migration for every new value,
which is exactly the rigidity we were asked to avoid for roles; keeping the
columns as text means the vocabulary can grow in a data-only migration while
Pydantic enforces the contract at the API boundary.
"""
from enum import Enum


class StrEnum(str, Enum):
    """str-valued enum so instances serialise as plain JSON strings."""

    def __str__(self) -> str:  # pragma: no cover - trivial
        return str(self.value)


class ContentStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class DataSource(StrEnum):
    PLACEHOLDER = "placeholder"
    CMS = "cms"


class EventCategory(StrEnum):
    SNAN_PARVA = "snan_parva"
    RELIGIOUS = "religious"
    AARTI = "aarti"
    AKHADA = "akhada"
    CULTURAL = "cultural"
    GOVERNMENT = "government"


class GhatStatus(StrEnum):
    OPEN = "open"
    RESTRICTED = "restricted"
    CLOSED = "closed"


class EmergencyCategory(StrEnum):
    POLICE = "police"
    AMBULANCE = "ambulance"
    FIRE = "fire"
    MEDICAL = "medical"
    WOMEN_CHILD = "women_child"
    DISASTER_MGMT = "disaster_mgmt"
    HELP_CENTER = "help_center"


class AnnouncementPriority(StrEnum):
    NORMAL = "normal"
    IMPORTANT = "important"
    CRITICAL = "critical"


class SosSituationCategory(StrEnum):
    MEDICAL = "medical"
    SECURITY = "security"
    FIRE = "fire"
    LOST_PERSON = "lost_person"
    OTHER = "other"


class LostFoundReportType(StrEnum):
    LOST = "lost"
    FOUND = "found"


class LostFoundCategory(StrEnum):
    BAG = "bag"
    DOCUMENTS = "documents"
    PHONE = "phone"
    JEWELLERY = "jewellery"
    CHILD_ITEM = "child_item"
    OTHER = "other"


class LostFoundStatus(StrEnum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    MATCHED = "matched"
    CLOSED = "closed"
    REJECTED = "rejected"


class MissingPersonStatus(StrEnum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    RESOLVED = "resolved"
    CLOSED = "closed"


class RoleName(StrEnum):
    """
    Seeded subset of PRD section 29. The full list lives in the `roles` table,
    not in this enum — these constants exist only so application code can refer
    to the three roles Sprint 1 actually gates on without magic strings.
    """
    SUPER_ADMIN = "super_admin"
    CONTENT_MANAGER = "content_manager"
    PUBLIC_USER = "public_user"


#: Roles permitted to reach /api/v1/admin/*.
ADMIN_ROLE_NAMES: frozenset[str] = frozenset(
    {RoleName.SUPER_ADMIN.value, RoleName.CONTENT_MANAGER.value}
)
