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
    #: Computed on request from other rows' own data_source, not authored and
    #: not a fixed seed value - see app/services/planner.py.
    GENERATED = "generated"


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


class TransportMode(StrEnum):
    CAR = "car"
    BUS = "bus"
    TRAIN = "train"
    WALKING = "walking"
    OTHER = "other"


class AccommodationPreference(StrEnum):
    BUDGET = "budget"
    MID_RANGE = "mid_range"
    PREMIUM = "premium"
    DHARAMSHALA = "dharamshala"
    NOT_NEEDED = "not_needed"


class AgeGroup(StrEnum):
    INFANT = "infant"
    CHILD = "child"
    ADULT = "adult"
    SENIOR = "senior"


class PilgrimInterest(StrEnum):
    SPIRITUAL = "spiritual"
    CULTURAL = "cultural"
    HISTORICAL = "historical"
    FAMILY_FRIENDLY = "family_friendly"
    PHOTOGRAPHY = "photography"


class AccessibilityRequirement(StrEnum):
    WHEELCHAIR = "wheelchair"
    VISUAL_IMPAIRMENT = "visual_impairment"
    HEARING_IMPAIRMENT = "hearing_impairment"
    ELDERLY_MOBILITY = "elderly_mobility"


class ParkingType(StrEnum):
    BUS = "bus"
    TWO_WHEELER = "two_wheeler"
    FOUR_WHEELER = "four_wheeler"
    ACCESSIBLE = "accessible"


class AccommodationType(StrEnum):
    HOTEL = "hotel"
    DHARAMSHALA = "dharamshala"
    ASHRAM = "ashram"
    TENT_CAMP = "tent_camp"
    GOVERNMENT = "government"


class AccommodationPriceTier(StrEnum):
    BUDGET = "budget"
    MID_RANGE = "mid_range"
    PREMIUM = "premium"


class EssentialServiceCategory(StrEnum):
    FOOD_SERVICE = "food_service"
    BHANDARA = "bhandara"
    DRINKING_WATER = "drinking_water"
    TOILET = "toilet"
    CHANGING_FACILITY = "changing_facility"


class CrowdDensityLevel(StrEnum):
    """Aggregate zone-level crowd band (PRD section 10) - never a per-person count."""

    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"


class CrowdEstimatedCountBand(StrEnum):
    """Coarse headcount range for operational planning, never an exact figure."""

    UNDER_500 = "under_500"
    FROM_500_TO_2000 = "500_to_2000"
    FROM_2000_TO_10000 = "2000_to_10000"
    OVER_10000 = "over_10000"


class CrowdReadingSource(StrEnum):
    """Every value here is an operator/admin action - never a live sensor or CCTV feed."""

    OPERATOR_ENTERED = "operator_entered"
    MANUAL_ESTIMATE = "manual_estimate"


class IncidentCategory(StrEnum):
    MEDICAL = "medical"
    SECURITY = "security"
    FIRE = "fire"
    INFRASTRUCTURE = "infrastructure"
    CROWD = "crowd"
    OTHER = "other"


class IncidentPriority(StrEnum):
    """PRD Table 3. P1 is the most severe / fastest SLA, P4 the least."""

    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class IncidentStatus(StrEnum):
    """reported -> classified -> assigned -> in_response -> resolved -> closed."""

    REPORTED = "reported"
    CLASSIFIED = "classified"
    ASSIGNED = "assigned"
    IN_RESPONSE = "in_response"
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
