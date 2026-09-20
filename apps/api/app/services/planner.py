"""
Pilgrimage Planner generation (PRD section 7, Sprint 2).

Deterministic, rule-based scheduling over Sprint 1's own published master
data - deliberately NOT an AI/RAG feature (that is Roadmap 2.7, AI Assistant,
which carries its own governance requirements). Interests only reorder which
events surface first; they never filter temples or ghats out, because master
data carries no interest tagging yet and every one of the seeded temples is a
legitimate Simhastha destination regardless of a visitor's stated interest.
Nothing generated here is persisted.
"""
from __future__ import annotations

from datetime import datetime, time, timedelta, timezone

from sqlalchemy.orm import Session

from app.api.v1.helpers import published_rows
from app.core.notices import PLANNER_NOTICE
from app.models.content import Event, Ghat, Temple
from app.models.enums import DataSource, PilgrimInterest
from app.schemas.planner import (
    PlannerDayOut,
    PlannerEventOut,
    PlannerGhatOut,
    PlannerRequest,
    PlannerResponse,
    PlannerTempleOut,
)

#: Realistic per-day limits so a short trip does not "schedule" nine temples
#: into one day - the honest overflow goes to unscheduled_temples/ghats.
TEMPLES_PER_DAY_CAP = 3
GHATS_PER_DAY_CAP = 2

#: Only interests with a real structural signal in the data (Event.category)
#: reorder anything. The rest are recorded and disclosed, not silently ignored.
_INTEREST_EVENT_CATEGORIES: dict[PilgrimInterest, set[str]] = {
    PilgrimInterest.SPIRITUAL: {"snan_parva", "religious", "aarti"},
    PilgrimInterest.CULTURAL: {"cultural", "akhada", "government"},
}


def _transport_note(mode: str) -> str:
    return (
        f"Transport mode '{mode}' recorded. Route planning and live transport "
        "data are not available in this prototype (see product roadmap items "
        "2.2 and 2.4) - plan travel times using general local knowledge."
    )


def _accommodation_note(preference: str) -> str:
    return (
        f"Accommodation preference '{preference}' recorded. An accommodation "
        "directory is not available in this prototype (see product roadmap "
        "item 2.5)."
    )


def _accessibility_note(requirements: list[str]) -> str | None:
    if not requirements:
        return None
    return (
        f"Accessibility requirements recorded: {', '.join(requirements)}. "
        "Facility accessibility information in this prototype is unverified "
        "placeholder text - confirm accessibility locally before travel."
    )


def _interest_note(interests: list[PilgrimInterest]) -> str | None:
    if not interests:
        return None
    matched = [i for i in interests if _INTEREST_EVENT_CATEGORIES.get(i)]
    unmatched = [i for i in interests if i not in matched]
    parts = [f"Interests recorded: {', '.join(i.value for i in interests)}."]
    if matched:
        parts.append(
            f"Events are prioritised for: {', '.join(i.value for i in matched)}."
        )
    if unmatched:
        parts.append(
            "No content-matching signal exists yet for: "
            f"{', '.join(i.value for i in unmatched)} - every published "
            "temple, ghat and event for your dates is included regardless."
        )
    return " ".join(parts)


def generate_itinerary(db: Session, request: PlannerRequest) -> PlannerResponse:
    days_count = (request.departure_date - request.arrival_date).days + 1

    temples = db.execute(published_rows(Temple).order_by(Temple.id)).scalars().all()
    ghats = db.execute(published_rows(Ghat).order_by(Ghat.id)).scalars().all()

    event_categories: set[str] = set()
    for interest in request.interests:
        event_categories |= _INTEREST_EVENT_CATEGORIES.get(interest, set())

    range_start = datetime.combine(request.arrival_date, time.min, tzinfo=timezone.utc)
    range_end = datetime.combine(request.departure_date, time.max, tzinfo=timezone.utc)
    events_in_range = (
        db.execute(
            published_rows(Event)
            .where(Event.starts_at >= range_start, Event.starts_at <= range_end)
            .order_by(Event.starts_at)
        )
        .scalars()
        .all()
    )
    if event_categories:
        # Stable reorder: matched-category events first, everything else
        # after, both in their original chronological order.
        events_in_range = [
            e for e in events_in_range if e.category in event_categories
        ] + [e for e in events_in_range if e.category not in event_categories]

    days: list[PlannerDayOut] = []
    temple_cursor = 0
    ghat_cursor = 0
    for offset in range(days_count):
        day_date = request.arrival_date + timedelta(days=offset)
        day_temples = temples[temple_cursor : temple_cursor + TEMPLES_PER_DAY_CAP]
        temple_cursor += len(day_temples)
        day_ghats = ghats[ghat_cursor : ghat_cursor + GHATS_PER_DAY_CAP]
        ghat_cursor += len(day_ghats)
        day_events = [e for e in events_in_range if e.starts_at.date() == day_date]

        days.append(
            PlannerDayOut(
                date=day_date,
                day_number=offset + 1,
                temples=[
                    PlannerTempleOut(
                        id=t.id,
                        slug=t.slug,
                        name=t.name,
                        short_description=t.short_description,
                    )
                    for t in day_temples
                ],
                ghats=[
                    PlannerGhatOut(id=g.id, slug=g.slug, name=g.name)
                    for g in day_ghats
                ],
                events=[
                    PlannerEventOut(
                        id=e.id,
                        slug=e.slug,
                        title=e.title,
                        category=e.category,
                        starts_at=e.starts_at,
                        venue_name=e.venue_name,
                    )
                    for e in day_events
                ],
                rest_period=not (day_temples or day_ghats or day_events),
            )
        )

    accessibility_values = [a.value for a in request.accessibility_requirements]

    return PlannerResponse(
        arrival_date=request.arrival_date,
        departure_date=request.departure_date,
        party_size=request.party_size,
        age_groups=[a.value for a in request.age_groups],
        transport_mode=request.transport_mode.value,
        accommodation_preference=request.accommodation_preference.value,
        interests=[i.value for i in request.interests],
        accessibility_requirements=accessibility_values,
        days=days,
        unscheduled_temples=[
            PlannerTempleOut(
                id=t.id, slug=t.slug, name=t.name, short_description=t.short_description
            )
            for t in temples[temple_cursor:]
        ],
        unscheduled_ghats=[
            PlannerGhatOut(id=g.id, slug=g.slug, name=g.name)
            for g in ghats[ghat_cursor:]
        ],
        transport_note=_transport_note(request.transport_mode.value),
        accommodation_note=_accommodation_note(request.accommodation_preference.value),
        accessibility_note=_accessibility_note(accessibility_values),
        interest_note=_interest_note(request.interests),
        data_source=DataSource.GENERATED.value,
        prototype_notice=PLANNER_NOTICE,
        generated_at=datetime.now(timezone.utc),
    )
