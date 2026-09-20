"""Pilgrimage Planner API (PRD section 7, Sprint 2, contract section 10)."""
from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient

# Matches app/seed.py's SEASON_START (2028-04-09) so requests overlap real
# seeded events instead of an empty date range.
ARRIVAL = date(2028, 4, 9)


def _payload(**overrides) -> dict:
    payload = {
        "arrival_date": ARRIVAL.isoformat(),
        "departure_date": (ARRIVAL).isoformat(),
        "party_size": 4,
        "age_groups": ["adult", "senior"],
        "transport_mode": "car",
        "accommodation_preference": "budget",
        "interests": [],
        "accessibility_requirements": [],
    }
    payload.update(overrides)
    return payload


def test_generate_itinerary_returns_expected_shape(client: TestClient):
    response = client.post("/api/v1/planner/itinerary", json=_payload())
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["data_source"] == "generated"
    assert "not an AI/RAG assistant" not in body["prototype_notice"]
    assert "Demo prototype" in body["prototype_notice"]
    assert len(body["days"]) == 1
    assert body["days"][0]["day_number"] == 1
    assert body["days"][0]["date"] == ARRIVAL.isoformat()


def test_one_day_trip_caps_temples_and_ghats_and_discloses_the_rest(
    client: TestClient,
):
    body = client.post("/api/v1/planner/itinerary", json=_payload()).json()
    day = body["days"][0]
    assert len(day["temples"]) <= 3
    assert len(day["ghats"]) <= 2
    # Nine seeded temples, capped at 3/day -> six left over, disclosed rather
    # than silently dropped.
    assert len(body["unscheduled_temples"]) == 9 - len(day["temples"])


def test_multi_day_trip_spreads_temples_across_days(client: TestClient):
    body = client.post(
        "/api/v1/planner/itinerary",
        json=_payload(departure_date=(date(2028, 4, 12)).isoformat()),
    ).json()
    assert len(body["days"]) == 4
    all_temple_ids = [
        t["id"] for day in body["days"] for t in day["temples"]
    ]
    assert len(all_temple_ids) == len(set(all_temple_ids)), "no temple repeats"
    # Four days at up to 3/day covers all nine seeded temples.
    assert len(body["unscheduled_temples"]) == 0


def test_seeded_event_on_the_arrival_day_is_included(client: TestClient):
    """app/seed.py seeds first-shahi-snan at SEASON_START (2028-04-09)."""
    body = client.post("/api/v1/planner/itinerary", json=_payload()).json()
    event_slugs = {e["slug"] for e in body["days"][0]["events"]}
    assert "first-shahi-snan" in event_slugs


def test_spiritual_interest_prioritises_matching_event_categories(
    client: TestClient,
):
    body = client.post(
        "/api/v1/planner/itinerary",
        json=_payload(
            departure_date=date(2028, 4, 21).isoformat(),
            interests=["spiritual", "photography"],
        ),
    ).json()
    assert "Interests recorded" in body["interest_note"]
    assert "spiritual" in body["interest_note"]
    assert "photography" in body["interest_note"]
    assert "No content-matching signal exists yet for: photography" in body["interest_note"]


def test_accessibility_requirements_are_echoed_with_a_disclosure(client: TestClient):
    body = client.post(
        "/api/v1/planner/itinerary",
        json=_payload(accessibility_requirements=["wheelchair"]),
    ).json()
    assert body["accessibility_requirements"] == ["wheelchair"]
    assert "unverified placeholder" in body["accessibility_note"]


def test_no_accessibility_requirements_means_no_note(client: TestClient):
    body = client.post("/api/v1/planner/itinerary", json=_payload()).json()
    assert body["accessibility_note"] is None


def test_rest_period_flagged_when_trip_outruns_seeded_content(client: TestClient):
    body = client.post(
        "/api/v1/planner/itinerary",
        json=_payload(
            arrival_date=date(2028, 4, 9).isoformat(),
            departure_date=date(2028, 4, 30).isoformat(),
        ),
    ).json()
    assert any(day["rest_period"] for day in body["days"])


def test_departure_before_arrival_is_rejected(client: TestClient):
    response = client.post(
        "/api/v1/planner/itinerary",
        json=_payload(departure_date=date(2028, 4, 1).isoformat()),
    )
    assert response.status_code == 422


def test_trip_longer_than_thirty_days_is_rejected(client: TestClient):
    response = client.post(
        "/api/v1/planner/itinerary",
        json=_payload(departure_date=date(2028, 6, 1).isoformat()),
    )
    assert response.status_code == 422


def test_unknown_enum_values_are_rejected(client: TestClient):
    assert (
        client.post(
            "/api/v1/planner/itinerary", json=_payload(transport_mode="rocket")
        ).status_code
        == 422
    )


def test_party_size_must_be_positive(client: TestClient):
    assert (
        client.post(
            "/api/v1/planner/itinerary", json=_payload(party_size=0)
        ).status_code
        == 422
    )


def test_unexpected_fields_are_rejected(client: TestClient):
    assert (
        client.post(
            "/api/v1/planner/itinerary", json=_payload(reporter_name="should not exist")
        ).status_code
        == 422
    )


def test_nothing_is_persisted(client: TestClient):
    """No admin/list surface exists for planner requests - stateless by design."""
    assert client.get("/api/v1/planner/itinerary").status_code in {404, 405}
    assert client.get("/api/v1/admin/planner").status_code in {404, 405}
