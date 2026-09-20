"""Command Center overview API (PRD section 24)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

OVERVIEW_PATH = "/api/v1/command-center/overview"
KNOWN_ZONE_SLUG = "ghat-zone-central"


def _submit_lost_found(client: TestClient) -> str:
    response = client.post(
        "/api/v1/lost-found",
        json={
            "report_type": "lost",
            "category": "bag",
            "description": "A brown backpack lost near the ghat steps.",
            "reporter_phone": "9990001111",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["case_reference"]


def _submit_missing_person(client: TestClient) -> str:
    response = client.post(
        "/api/v1/missing-person",
        json={
            "person_name": "Test Person",
            "reporter_phone": "9990002222",
            "consent_given": True,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["case_reference"]


def _submit_sos(client: TestClient) -> str:
    response = client.post(
        "/api/v1/emergency/sos",
        json={"situation_category": "other", "consent_given": True},
    )
    assert response.status_code == 201, response.text
    return response.json()["case_reference"]


def _lost_found_admin_id(client: TestClient, admin_headers: dict, reference: str) -> int:
    rows = client.get("/api/v1/admin/lost-found", headers=admin_headers).json()["items"]
    return next(row["id"] for row in rows if row["case_reference"] == reference)


def test_overview_requires_admin_401_anonymous(client: TestClient):
    assert client.get(OVERVIEW_PATH).status_code == 401


def test_overview_rejects_public_user_with_403(
    client: TestClient, public_user_token: str
):
    response = client.get(
        OVERVIEW_PATH, headers={"Authorization": f"Bearer {public_user_token}"}
    )
    assert response.status_code == 403


def test_overview_shape_has_three_distinct_sections(
    client: TestClient, admin_headers: dict
):
    response = client.get(OVERVIEW_PATH, headers=admin_headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert "Demo prototype" in body["prototype_notice"]
    assert set(body.keys()) >= {
        "observed",
        "recommendations",
        "human_decisions",
        "generated_at",
        "prototype_notice",
    }


def test_recommendations_section_is_always_empty_and_labelled(
    client: TestClient, admin_headers: dict
):
    body = client.get(OVERVIEW_PATH, headers=admin_headers).json()
    recs = body["recommendations"]
    assert recs["available"] is False
    assert recs["items"] == []
    assert "Not available in this prototype" in recs["note"]


def test_observed_zones_include_latest_crowd_reading(
    client: TestClient, admin_headers: dict
):
    create = client.post(
        f"/api/v1/crowd/zones/{KNOWN_ZONE_SLUG}/readings",
        json={"density_level": "red", "source": "manual_estimate"},
        headers=admin_headers,
    )
    assert create.status_code == 201, create.text

    body = client.get(OVERVIEW_PATH, headers=admin_headers).json()
    zones = {z["zone_slug"]: z for z in body["observed"]["zones"]}
    assert KNOWN_ZONE_SLUG in zones
    assert zones[KNOWN_ZONE_SLUG]["latest_crowd_reading"]["density_level"] == "red"
    # A zone with no reading yet must not fabricate one.
    other_zone = next(
        z for slug, z in zones.items() if slug != KNOWN_ZONE_SLUG
    )
    assert other_zone["latest_crowd_reading"] is None


def test_open_case_totals_increase_when_cases_are_submitted(
    client: TestClient, admin_headers: dict
):
    before = client.get(OVERVIEW_PATH, headers=admin_headers).json()["observed"][
        "case_totals"
    ]

    _submit_sos(client)
    _submit_lost_found(client)
    _submit_missing_person(client)

    after = client.get(OVERVIEW_PATH, headers=admin_headers).json()["observed"][
        "case_totals"
    ]
    assert after["open_sos_incidents"] == before["open_sos_incidents"] + 1
    assert after["open_lost_found_cases"] == before["open_lost_found_cases"] + 1
    assert after["open_missing_person_cases"] == before["open_missing_person_cases"] + 1


def test_case_totals_note_discloses_platform_wide_not_per_zone(
    client: TestClient, admin_headers: dict
):
    body = client.get(OVERVIEW_PATH, headers=admin_headers).json()
    note = body["observed"]["case_totals_note"]
    assert "not per zone" in note.lower() or "platform-wide" in note.lower()


def test_rejecting_a_lost_found_case_removes_it_from_open_total(
    client: TestClient, admin_headers: dict
):
    reference = _submit_lost_found(client)
    before = client.get(OVERVIEW_PATH, headers=admin_headers).json()["observed"][
        "case_totals"
    ]["open_lost_found_cases"]

    item_id = _lost_found_admin_id(client, admin_headers, reference)
    patch = client.patch(
        f"/api/v1/admin/lost-found/{item_id}",
        json={"status": "rejected"},
        headers=admin_headers,
    )
    assert patch.status_code == 200, patch.text

    after = client.get(OVERVIEW_PATH, headers=admin_headers).json()["observed"][
        "case_totals"
    ]["open_lost_found_cases"]
    assert after == before - 1


def test_human_decisions_reflect_admin_set_status(
    client: TestClient, admin_headers: dict
):
    reference = _submit_lost_found(client)
    item_id = _lost_found_admin_id(client, admin_headers, reference)
    client.patch(
        f"/api/v1/admin/lost-found/{item_id}",
        json={"status": "under_review"},
        headers=admin_headers,
    )

    body = client.get(OVERVIEW_PATH, headers=admin_headers).json()
    decisions = body["human_decisions"]
    assert "human decision" in decisions["note"].lower()
    matches = [
        d
        for d in decisions["recent_status_decisions"]
        if d["case_reference"] == reference
    ]
    assert matches, "expected the updated case to appear in recent human decisions"
    assert matches[0]["status"] == "under_review"
    assert matches[0]["entity_type"] == "lost_found_case"


def test_human_decisions_never_leak_personal_fields(
    client: TestClient, admin_headers: dict
):
    _submit_lost_found(client)
    body = client.get(OVERVIEW_PATH, headers=admin_headers).json()
    raw = str(body["human_decisions"]).lower()
    assert "9990001111" not in raw
    assert "brown backpack" not in raw


def test_critical_published_unexpired_announcement_is_surfaced(
    client: TestClient, admin_headers: dict
):
    create = client.post(
        "/api/v1/admin/announcements",
        json={
            "slug": "cc-test-critical-alert",
            "title": "Test critical alert",
            "body": "Test body for command centre visibility.",
            "priority": "critical",
        },
        headers=admin_headers,
    )
    assert create.status_code == 201, create.text
    announcement_id = create.json()["id"]

    publish = client.patch(
        f"/api/v1/admin/announcements/{announcement_id}",
        json={"status": "published", "published_at": "2028-04-01T00:00:00Z"},
        headers=admin_headers,
    )
    assert publish.status_code == 200, publish.text

    body = client.get(OVERVIEW_PATH, headers=admin_headers).json()
    slugs = {a["slug"] for a in body["observed"]["critical_announcements"]}
    assert "cc-test-critical-alert" in slugs


def test_draft_critical_announcement_is_not_surfaced(
    client: TestClient, admin_headers: dict
):
    create = client.post(
        "/api/v1/admin/announcements",
        json={
            "slug": "cc-test-draft-alert",
            "title": "Draft alert",
            "body": "Should not appear while still a draft.",
            "priority": "critical",
        },
        headers=admin_headers,
    )
    assert create.status_code == 201, create.text

    body = client.get(OVERVIEW_PATH, headers=admin_headers).json()
    slugs = {a["slug"] for a in body["observed"]["critical_announcements"]}
    assert "cc-test-draft-alert" not in slugs
