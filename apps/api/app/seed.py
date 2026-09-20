"""
Idempotent development seed data.

Run it with::

    docker compose --env-file .env -f infra/docker-compose.yml exec api python -m app.seed

HONESTY RULES THIS FILE OBEYS
=============================

1. **No invented facts presented as fact.** Darshan timings, aarti schedules,
   accessibility details and transport guidance are explicitly marked
   placeholder text. This prototype has no relationship with any temple
   administration, and a pilgrim planning a journey around a fabricated aarti
   time would be actively harmed by it. Every seeded row therefore carries
   ``data_source = "placeholder"`` and ``verified = False``.

2. **Emergency phone numbers are obviously fake.** Every seeded number follows
   the ``+91-00000-000NN`` pattern. Real Indian emergency numbers (100, 102,
   108, 112) and real police-station numbers are never written here. A user
   must never be able to tap-to-call a number this prototype implies is
   staffed, and a number that looks real is exactly the thing that gets dialled
   in a panic.

3. **Coordinates are approximate.** Latitude/longitude are taken from publicly
   known locations of Ujjain landmarks so the map renders somewhere meaningful.
   They are not survey-grade and have not been checked against any cadastral or
   government source; they must be verified before any operational use. Two
   entries - ``84-mahadev`` and ``panchkroshi-yatra`` - have NO coordinates on
   purpose: both are multi-site circuits rather than single buildings, and
   pinning them to one point would misrepresent what they are.

4. **Event dates are indicative.** The official Simhastha 2028 calendar has not
   been published. Seeded dates are plausible placeholders for UI development,
   flagged as such in every summary, and must not be quoted as scheduling
   information.

Re-running is safe: every record is matched on its natural key (slug, username,
or name+category) and updated in place rather than re-inserted.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.content import Announcement, Event, Ghat, Temple, Zone
from app.models.emergency import EmergencyService
from app.models.enums import (
    AnnouncementPriority,
    ContentStatus,
    DataSource,
    EmergencyCategory,
    EventCategory,
    GhatStatus,
    RoleName,
)
from app.models.user import Role, User

PLACEHOLDER_TIMINGS = (
    "Placeholder — darshan timings to be confirmed by temple authority."
)
PLACEHOLDER_AARTI = (
    "Placeholder — aarti schedule not confirmed by temple authority."
)
PLACEHOLDER_ACCESS = (
    "Placeholder — accessibility details not yet verified."
)
PLACEHOLDER_TRANSPORT = (
    "Placeholder transport guidance — routes and services not yet confirmed."
)
INDICATIVE_DATE_NOTE = (
    "Indicative placeholder date — the official Simhastha 2028 calendar has "
    "not been published."
)

# Simhastha 2028 is expected in the April-May window. These anchors exist only
# so the calendar UI has a realistic spread of dates to lay out.
SEASON_START = datetime(2028, 4, 9, 4, 30, tzinfo=timezone.utc)


def _upsert(
    db: Session,
    model: type,
    match: dict[str, Any],
    values: dict[str, Any],
) -> Any:
    """
    Insert or update one row, matched on its natural key.

    Idempotency matters here beyond convenience: a developer re-running the
    seed after a partial failure must not end up with duplicate temples or a
    unique-index explosion that leaves the database half-populated.
    """
    stmt = select(model)
    for key, value in match.items():
        stmt = stmt.where(getattr(model, key) == value)
    row = db.execute(stmt).scalar_one_or_none()

    if row is None:
        row = model(**match, **values)
        db.add(row)
    else:
        for key, value in values.items():
            setattr(row, key, value)
    db.flush()
    return row


# --------------------------------------------------------------------------
# Roles and users
# --------------------------------------------------------------------------
def seed_roles(db: Session) -> dict[str, Role]:
    """
    Seed the three roles Sprint 1 gates on.

    PRD section 29 lists nine. The other six are deliberately absent rather
    than stubbed: they are rows in this table, so adding department_admin or
    police_admin later is an INSERT, not a migration.
    """
    definitions = [
        (
            RoleName.SUPER_ADMIN.value,
            "Full administrative access across all modules.",
            True,
        ),
        (
            RoleName.CONTENT_MANAGER.value,
            "Creates and publishes events, announcements, temples and ghats.",
            True,
        ),
        (
            RoleName.PUBLIC_USER.value,
            "Ordinary pilgrim account. No administrative access whatsoever.",
            False,
        ),
    ]
    roles: dict[str, Role] = {}
    for name, description, is_admin in definitions:
        roles[name] = _upsert(
            db,
            Role,
            {"name": name},
            {"description": description, "is_admin": is_admin},
        )
    return roles


def seed_users(db: Session, roles: dict[str, Role]) -> list[tuple[str, str, str]]:
    """Create the development logins. Returns (username, password, role)."""
    accounts = [
        (
            settings.SEED_SUPER_ADMIN_USERNAME,
            settings.SEED_SUPER_ADMIN_PASSWORD,
            "Sprint 1 Admin",
            RoleName.SUPER_ADMIN.value,
        ),
        (
            settings.SEED_CONTENT_MANAGER_USERNAME,
            settings.SEED_CONTENT_MANAGER_PASSWORD,
            "Sprint 1 Content Manager",
            RoleName.CONTENT_MANAGER.value,
        ),
        (
            "pilgrim",
            "Pilgrim@2028",
            "Sprint 1 Public User",
            RoleName.PUBLIC_USER.value,
        ),
    ]
    created: list[tuple[str, str, str]] = []
    for username, password, full_name, role_name in accounts:
        _upsert(
            db,
            User,
            {"username": username},
            {
                "full_name": full_name,
                # Hashed with bcrypt via passlib. The plaintext exists only in
                # settings and in the summary printed below.
                "hashed_password": hash_password(password),
                "role_id": roles[role_name].id,
                "is_active": True,
            },
        )
        created.append((username, password, role_name))
    return created


# --------------------------------------------------------------------------
# Master data
# --------------------------------------------------------------------------
def seed_zones(db: Session) -> dict[str, Zone]:
    definitions = [
        ("ghat-zone-central", "Central Ghat Zone", "ghat", 23.1852, 75.7684),
        ("temple-zone-mahakal", "Mahakal Temple Zone", "temple", 23.1828, 75.7682),
        ("transit-zone-north", "Northern Transit Zone", "transit", 23.2030, 75.7870),
    ]
    zones: dict[str, Zone] = {}
    for slug, name, zone_type, lat, lon in definitions:
        zones[slug] = _upsert(
            db,
            Zone,
            {"slug": slug},
            {
                "name": name,
                "zone_type": zone_type,
                "description": (
                    "Sample operational zone for schema demonstration. No crowd, "
                    "traffic or capacity data is associated with it."
                ),
                "latitude": lat,
                "longitude": lon,
            },
        )
    return zones


def seed_temples(db: Session, zones: dict[str, Zone]) -> int:
    """The nine temples named in PRD section 13, with slugs fixed by D-04."""
    mahakal_zone = zones["temple-zone-mahakal"].id

    definitions: list[dict[str, Any]] = [
        {
            "slug": "mahakaleshwar",
            "name": "Mahakaleshwar Jyotirlinga",
            "short_description": "One of the twelve Jyotirlingas, on the bank of the Shipra.",
            "significance": (
                "Mahakaleshwar is one of the twelve Jyotirlinga shrines and the "
                "principal temple of Ujjain. Detailed significance text is "
                "pending review by the temple administration."
            ),
            "address": "Jaisinghpura, Ujjain, Madhya Pradesh",
            "latitude": 23.1828,
            "longitude": 75.7682,
            "zone_id": mahakal_zone,
        },
        {
            "slug": "kal-bhairav",
            "name": "Kal Bhairav Temple",
            "short_description": "Temple of Kal Bhairav, guardian deity of Ujjain.",
            "significance": (
                "One of Ujjain's most visited shrines. Full significance text "
                "is pending review by the temple administration."
            ),
            "address": "Bhairavgarh, Ujjain, Madhya Pradesh",
            "latitude": 23.1975,
            "longitude": 75.7607,
        },
        {
            "slug": "harsiddhi",
            "name": "Harsiddhi Temple",
            "short_description": "Shakti Peetha near the Mahakaleshwar precinct.",
            "significance": (
                "Counted among the Shakti Peethas. Full significance text is "
                "pending review by the temple administration."
            ),
            "address": "Near Rudra Sagar, Ujjain, Madhya Pradesh",
            "latitude": 23.1806,
            "longitude": 75.7676,
            "zone_id": mahakal_zone,
        },
        {
            "slug": "mangalnath",
            "name": "Mangalnath Temple",
            "short_description": "Temple associated with the planet Mangal (Mars).",
            "significance": (
                "Traditionally regarded as the birthplace of Mangal. Full "
                "significance text is pending review by the temple administration."
            ),
            "address": "Mangalnath Road, Ujjain, Madhya Pradesh",
            "latitude": 23.2029,
            "longitude": 75.7876,
            "zone_id": zones["transit-zone-north"].id,
        },
        {
            "slug": "gadkalika",
            "name": "Gadkalika Temple",
            "short_description": "Ancient temple of Goddess Kalika.",
            "significance": (
                "An ancient Kalika shrine associated with the poet Kalidasa. "
                "Full significance text is pending review by the temple "
                "administration."
            ),
            "address": "Gadkalika area, Ujjain, Madhya Pradesh",
            "latitude": 23.1949,
            "longitude": 75.7719,
        },
        {
            "slug": "chintaman-ganesh",
            "name": "Chintaman Ganesh Temple",
            "short_description": "One of the oldest Ganesh temples in the region.",
            "significance": (
                "A long-established Ganesh shrine south-west of the city "
                "centre. Full significance text is pending review by the temple "
                "administration."
            ),
            "address": "Chintaman, Ujjain, Madhya Pradesh",
            "latitude": 23.1610,
            "longitude": 75.7420,
        },
        {
            "slug": "sandipani-ashram",
            "name": "Sandipani Ashram",
            "short_description": "Traditional site of the ashram of sage Sandipani.",
            "significance": (
                "Associated in tradition with the education of Krishna and "
                "Sudama. Full significance text is pending review."
            ),
            "address": "Mangalnath Road, Ujjain, Madhya Pradesh",
            "latitude": 23.1955,
            "longitude": 75.7847,
            "zone_id": zones["transit-zone-north"].id,
        },
        {
            "slug": "84-mahadev",
            "name": "84 Mahadev",
            "short_description": (
                "A circuit of eighty-four Shiva shrines distributed across Ujjain."
            ),
            "significance": (
                "84 Mahadev is a pilgrimage circuit of eighty-four separate "
                "Shiva shrines, not a single temple building. Individual shrine "
                "locations and the recommended order of visit are pending "
                "compilation from an authoritative source."
            ),
            "address": "Multiple shrines across Ujjain, Madhya Pradesh",
            # Deliberately no coordinates: this is a distributed circuit and a
            # single pin would tell a pilgrim to go to the wrong place.
            "latitude": None,
            "longitude": None,
        },
        {
            "slug": "panchkroshi-yatra",
            "name": "Panchkroshi Yatra",
            "short_description": (
                "A traditional circumambulatory pilgrimage route around Ujjain."
            ),
            "significance": (
                "Panchkroshi Yatra is a multi-day circumambulatory route with "
                "several halting stations, not a single site. The route, halt "
                "points and schedule are pending confirmation from the district "
                "administration."
            ),
            "address": "Circumambulatory route around Ujjain, Madhya Pradesh",
            # Deliberately no coordinates: this is a route, not a point.
            "latitude": None,
            "longitude": None,
        },
    ]

    for item in definitions:
        slug = item.pop("slug")
        _upsert(
            db,
            Temple,
            {"slug": slug},
            {
                **item,
                "timings": PLACEHOLDER_TIMINGS,
                "aarti_schedule": PLACEHOLDER_AARTI,
                "transport_info": PLACEHOLDER_TRANSPORT,
                "accessibility_info": PLACEHOLDER_ACCESS,
                "image_url": None,
                "status": ContentStatus.PUBLISHED.value,
                "data_source": DataSource.PLACEHOLDER.value,
                # Nothing in this prototype has been signed off by a temple
                # authority, so the verified badge is never granted at seed time.
                "verified": False,
            },
        )
    return len(definitions)


def seed_ghats(db: Session, zones: dict[str, Zone]) -> int:
    central = zones["ghat-zone-central"].id
    definitions = [
        {
            "slug": "ram-ghat",
            "name": "Ram Ghat",
            "description": "The principal bathing ghat on the Shipra in Ujjain.",
            "latitude": 23.1852,
            "longitude": 75.7684,
            "facilities": ["changing_rooms", "drinking_water", "toilets"],
            "zone_id": central,
        },
        {
            "slug": "mangalnath-ghat",
            "name": "Mangalnath Ghat",
            "description": "Bathing ghat adjoining the Mangalnath temple area.",
            "latitude": 23.2035,
            "longitude": 75.7880,
            "facilities": ["drinking_water", "toilets"],
        },
        {
            "slug": "siddhavat-ghat",
            "name": "Siddhavat Ghat",
            "description": "Ghat near the Siddhavat site on the Shipra.",
            "latitude": 23.2113,
            "longitude": 75.7997,
            "facilities": ["drinking_water"],
        },
        {
            "slug": "narsingh-ghat",
            "name": "Narsingh Ghat",
            "description": "Bathing ghat on the Shipra near the city centre.",
            "latitude": 23.1880,
            "longitude": 75.7700,
            "facilities": ["changing_rooms", "drinking_water"],
            "zone_id": central,
        },
        {
            "slug": "triveni-ghat",
            "name": "Triveni Ghat",
            "description": "Ghat at the southern approach to the Shipra.",
            "latitude": 23.1560,
            "longitude": 75.7550,
            "facilities": ["drinking_water", "toilets"],
        },
    ]
    for item in definitions:
        slug = item.pop("slug")
        _upsert(
            db,
            Ghat,
            {"slug": slug},
            {
                **item,
                "bathing_info": (
                    "Placeholder bathing guidance — safe-bathing areas, water "
                    "depth and timing advice are pending confirmation by the "
                    "district administration."
                ),
                "accessibility_info": PLACEHOLDER_ACCESS,
                "image_url": None,
                # Seeded as 'open' because that is the neutral default, not
                # because anyone has inspected the ghat today.
                "operational_status": GhatStatus.OPEN.value,
                "advisory": None,
                # Never populated: no crowd or CCTV feed exists (see the ghat
                # status endpoint, which cannot emit a crowd level at all).
                "crowd_level": None,
                "status": ContentStatus.PUBLISHED.value,
                "data_source": DataSource.PLACEHOLDER.value,
            },
        )
    return len(definitions)


def seed_events(db: Session) -> int:
    """Sample events spanning every value of the category enum."""
    definitions = [
        (
            "first-shahi-snan",
            "First Shahi Snan",
            EventCategory.SNAN_PARVA,
            SEASON_START,
            timedelta(hours=8),
            "Ram Ghat",
            23.1852,
            75.7684,
        ),
        (
            "second-shahi-snan",
            "Second Shahi Snan",
            EventCategory.SNAN_PARVA,
            SEASON_START + timedelta(days=12),
            timedelta(hours=8),
            "Ram Ghat",
            23.1852,
            75.7684,
        ),
        (
            "mahakaleshwar-bhasma-aarti",
            "Mahakaleshwar Bhasma Aarti",
            EventCategory.AARTI,
            SEASON_START + timedelta(days=1),
            timedelta(hours=2),
            "Mahakaleshwar Jyotirlinga",
            23.1828,
            75.7682,
        ),
        (
            "akhada-peshwai-procession",
            "Akhada Peshwai Procession",
            EventCategory.AKHADA,
            SEASON_START + timedelta(days=3),
            timedelta(hours=6),
            "Ujjain city route",
            None,
            None,
        ),
        (
            "shipra-aarti-cultural-evening",
            "Shipra Cultural Evening",
            EventCategory.CULTURAL,
            SEASON_START + timedelta(days=5, hours=13),
            timedelta(hours=3),
            "Ram Ghat",
            23.1852,
            75.7684,
        ),
        (
            "harsiddhi-deep-stambh-darshan",
            "Harsiddhi Deep Stambh Darshan",
            EventCategory.RELIGIOUS,
            SEASON_START + timedelta(days=6, hours=13),
            timedelta(hours=2),
            "Harsiddhi Temple",
            23.1806,
            75.7676,
        ),
        (
            "district-administration-briefing",
            "District Administration Public Briefing",
            EventCategory.GOVERNMENT,
            SEASON_START + timedelta(days=2, hours=5),
            timedelta(hours=2),
            "Ujjain Collectorate",
            None,
            None,
        ),
    ]

    for (
        slug,
        title,
        category,
        starts_at,
        duration,
        venue,
        lat,
        lon,
    ) in definitions:
        _upsert(
            db,
            Event,
            {"slug": slug},
            {
                "title": title,
                "summary": f"{INDICATIVE_DATE_NOTE}",
                "description": (
                    f"Sample calendar entry for interface development. "
                    f"{INDICATIVE_DATE_NOTE} Timing, venue and participation "
                    "details have not been confirmed by any organising body."
                ),
                "category": category.value,
                "starts_at": starts_at,
                "ends_at": starts_at + duration,
                "venue_name": venue,
                "latitude": lat,
                "longitude": lon,
                "image_url": None,
                "status": ContentStatus.PUBLISHED.value,
                "data_source": DataSource.PLACEHOLDER.value,
            },
        )
    return len(definitions)


def seed_emergency_services(db: Session) -> int:
    """
    Sample directory entries across the category enum.

    EVERY phone number below is a deliberately invalid placeholder in the
    +91-00000-000NN pattern. Do not replace them with real numbers while this
    remains a prototype - the whole point is that a number here cannot connect
    anyone to anything.
    """
    definitions = [
        (
            "Ujjain Central Police Help Point (demo)",
            EmergencyCategory.POLICE,
            "+91-00000-00001",
            "Near Ram Ghat, Ujjain",
            23.1830,
            75.7690,
        ),
        (
            "Mahakal Precinct Police Post (demo)",
            EmergencyCategory.POLICE,
            "+91-00000-00002",
            "Mahakaleshwar temple precinct, Ujjain",
            23.1825,
            75.7679,
        ),
        (
            "Shipra Ambulance Station (demo)",
            EmergencyCategory.AMBULANCE,
            "+91-00000-00003",
            "Shipra riverside, Ujjain",
            23.1860,
            75.7695,
        ),
        (
            "Ujjain Fire Response Unit (demo)",
            EmergencyCategory.FIRE,
            "+91-00000-00004",
            "City centre, Ujjain",
            23.1795,
            75.7845,
        ),
        (
            "Temporary Medical Camp - Ram Ghat (demo)",
            EmergencyCategory.MEDICAL,
            "+91-00000-00005",
            "Ram Ghat approach road, Ujjain",
            23.1848,
            75.7688,
        ),
        (
            "Women and Child Help Desk (demo)",
            EmergencyCategory.WOMEN_CHILD,
            "+91-00000-00006",
            "Near Harsiddhi Temple, Ujjain",
            23.1810,
            75.7672,
        ),
        (
            "District Disaster Management Cell (demo)",
            EmergencyCategory.DISASTER_MGMT,
            "+91-00000-00007",
            "Ujjain Collectorate",
            23.1793,
            75.7849,
        ),
        (
            "Pilgrim Help Centre - Mangalnath (demo)",
            EmergencyCategory.HELP_CENTER,
            "+91-00000-00008",
            "Mangalnath Road, Ujjain",
            23.2030,
            75.7872,
        ),
    ]
    for name, category, phone, address, lat, lon in definitions:
        _upsert(
            db,
            EmergencyService,
            {"name": name, "category": category.value},
            {
                "phone": phone,
                "address": address,
                "latitude": lat,
                "longitude": lon,
                "hours": "24x7 (nominal — not an operational commitment)",
                "notes": (
                    "Seeded demo entry — not a real contact. The number above "
                    "is an intentionally invalid placeholder and connects to "
                    "nothing. In a real emergency, dial your local emergency "
                    "number directly."
                ),
                "status": ContentStatus.PUBLISHED.value,
                "data_source": DataSource.PLACEHOLDER.value,
            },
        )
    return len(definitions)


def seed_announcements(db: Session) -> int:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    definitions = [
        (
            "prototype-disclaimer",
            "About this prototype",
            (
                "This is a demonstration build of the Simhastha 2028 platform. "
                "It is not connected to police, medical, fire, CCTV or any "
                "government dispatch system. Information shown here is seeded "
                "placeholder content and must not be used to plan a journey or "
                "to seek help in an emergency."
            ),
            AnnouncementPriority.CRITICAL,
            now - timedelta(hours=2),
            None,
        ),
        (
            "shuttle-route-change",
            "Shuttle route change for Ram Ghat",
            (
                "Sample announcement for interface development. Shuttle routing "
                "information has not been issued by any transport authority."
            ),
            AnnouncementPriority.NORMAL,
            now - timedelta(hours=1),
            now + timedelta(days=30),
        ),
        (
            "ghat-safety-advisory",
            "General bathing safety advisory",
            (
                "Sample advisory for interface development. Real bathing safety "
                "guidance will be issued by the district administration and is "
                "not reproduced here."
            ),
            AnnouncementPriority.IMPORTANT,
            now - timedelta(minutes=30),
            now + timedelta(days=14),
        ),
    ]
    for slug, title, body, priority, published_at, expires_at in definitions:
        _upsert(
            db,
            Announcement,
            {"slug": slug},
            {
                "title": title,
                "body": body,
                "priority": priority.value,
                "published_at": published_at,
                "expires_at": expires_at,
                "status": ContentStatus.PUBLISHED.value,
                "data_source": DataSource.PLACEHOLDER.value,
            },
        )
    return len(definitions)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------
def run_seed(db: Session) -> dict[str, int]:
    roles = seed_roles(db)
    accounts = seed_users(db, roles)
    zones = seed_zones(db)

    counts = {
        "roles": len(roles),
        "users": len(accounts),
        "zones": len(zones),
        "temples": seed_temples(db, zones),
        "ghats": seed_ghats(db, zones),
        "events": seed_events(db),
        "emergency_services": seed_emergency_services(db),
        "announcements": seed_announcements(db),
    }
    db.commit()
    return {"counts": counts, "accounts": accounts}  # type: ignore[return-value]


def main() -> int:
    # Guard rail: these are well-known credentials printed to a terminal. They
    # belong in a development database and nowhere else.
    if settings.ENV.lower() not in {"development", "dev", "local", "test"}:
        print(
            f"Refusing to seed: ENV is '{settings.ENV}'. This script creates "
            "accounts with published default passwords and is for development "
            "databases only.",
            file=sys.stderr,
        )
        return 1

    with SessionLocal() as db:
        result = run_seed(db)

    counts = result["counts"]
    accounts = result["accounts"]

    print("\nSeed complete. Rows ensured (idempotent upsert):")
    for entity, count in counts.items():
        print(f"  {entity:<20} {count}")

    print("\nDevelopment login credentials:")
    print(f"  {'username':<12} {'password':<18} role")
    for username, password, role_name in accounts:
        print(f"  {username:<12} {password:<18} {role_name}")

    print(
        "\nReminders:\n"
        "  * All seeded content is placeholder data (data_source='placeholder').\n"
        "  * Temple timings, aarti schedules and accessibility text are NOT\n"
        "    authority-confirmed, and every temple has verified=false.\n"
        "  * Emergency directory phone numbers are intentionally invalid\n"
        "    (+91-00000-000NN) and connect to nothing.\n"
        "  * Coordinates are approximate public knowledge, not survey data.\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
