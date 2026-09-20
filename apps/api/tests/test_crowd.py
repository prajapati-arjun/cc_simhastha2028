"""Crowd Analytics API (PRD section 10, section 26)."""
from __future__ import annotations

from fastapi.testclient import TestClient

# Seeded by app/seed.py's seed_zones().
KNOWN_ZONE_SLUG = "ghat-zone-central"


def _reading_payload(**overrides) -> dict:
    payload = {
        "density_level": "yellow",
        "estimated_count_band": "500_to_2000",
        "source": "operator_entered",
    }
    payload.update(overrides)
    return payload


def test_list_crowd_zones_includes_every_seeded_zone_with_no_reading(
    client: TestClient,
):
    response = client.get("/api/v1/crowd/zones")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["total"] >= 3
    slugs = {item["zone_slug"] for item in body["items"]}
    assert KNOWN_ZONE_SLUG in slugs
    # No reading has been recorded yet -> disclosed as null, not fabricated.
    for item in body["items"]:
        assert item["latest_reading"] is None
        assert "Demo prototype" in item["prototype_notice"]


def test_get_crowd_zone_by_slug_with_no_readings(client: TestClient):
    response = client.get(f"/api/v1/crowd/zones/{KNOWN_ZONE_SLUG}")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["zone_slug"] == KNOWN_ZONE_SLUG
    assert body["latest_reading"] is None
    assert body["history"] == []


def test_get_crowd_zone_unknown_ref_is_404(client: TestClient):
    assert client.get("/api/v1/crowd/zones/not-a-real-zone").status_code == 404
    assert client.get("/api/v1/crowd/zones/999999").status_code == 404


def test_create_reading_requires_admin_401_anonymous(client: TestClient):
    response = client.post(
        f"/api/v1/crowd/zones/{KNOWN_ZONE_SLUG}/readings",
        json=_reading_payload(),
    )
    assert response.status_code == 401


def test_create_reading_rejects_public_user_with_403(
    client: TestClient, public_user_token: str
):
    response = client.post(
        f"/api/v1/crowd/zones/{KNOWN_ZONE_SLUG}/readings",
        json=_reading_payload(),
        headers={"Authorization": f"Bearer {public_user_token}"},
    )
    assert response.status_code == 403


def test_admin_can_record_a_reading_and_it_becomes_the_latest(
    client: TestClient, admin_headers: dict
):
    create_response = client.post(
        f"/api/v1/crowd/zones/{KNOWN_ZONE_SLUG}/readings",
        json=_reading_payload(density_level="orange"),
        headers=admin_headers,
    )
    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created["reading"]["density_level"] == "orange"
    assert created["reading"]["source"] == "operator_entered"
    assert created["reading"]["recorded_by_user_id"] is not None
    assert "Demo prototype" in created["prototype_notice"]

    detail_response = client.get(f"/api/v1/crowd/zones/{KNOWN_ZONE_SLUG}")
    detail = detail_response.json()
    assert detail["latest_reading"]["density_level"] == "orange"
    assert len(detail["history"]) == 1

    list_response = client.get("/api/v1/crowd/zones")
    listed = {
        item["zone_slug"]: item for item in list_response.json()["items"]
    }
    assert listed[KNOWN_ZONE_SLUG]["latest_reading"]["density_level"] == "orange"


def test_second_reading_becomes_latest_and_history_keeps_both(
    client: TestClient, admin_headers: dict
):
    client.post(
        f"/api/v1/crowd/zones/{KNOWN_ZONE_SLUG}/readings",
        json=_reading_payload(
            density_level="green", recorded_at="2028-04-01T06:00:00Z"
        ),
        headers=admin_headers,
    )
    client.post(
        f"/api/v1/crowd/zones/{KNOWN_ZONE_SLUG}/readings",
        json=_reading_payload(
            density_level="red", recorded_at="2028-04-02T06:00:00Z"
        ),
        headers=admin_headers,
    )

    detail = client.get(f"/api/v1/crowd/zones/{KNOWN_ZONE_SLUG}").json()
    assert detail["latest_reading"]["density_level"] == "red"
    assert len(detail["history"]) == 2
    # newest first
    assert detail["history"][0]["density_level"] == "red"
    assert detail["history"][1]["density_level"] == "green"


def test_unknown_density_level_is_rejected(
    client: TestClient, admin_headers: dict
):
    response = client.post(
        f"/api/v1/crowd/zones/{KNOWN_ZONE_SLUG}/readings",
        json=_reading_payload(density_level="lava"),
        headers=admin_headers,
    )
    assert response.status_code == 422


def test_unknown_source_is_rejected(client: TestClient, admin_headers: dict):
    response = client.post(
        f"/api/v1/crowd/zones/{KNOWN_ZONE_SLUG}/readings",
        json=_reading_payload(source="live_cctv_feed"),
        headers=admin_headers,
    )
    assert response.status_code == 422


def test_unexpected_fields_are_rejected(client: TestClient, admin_headers: dict):
    response = client.post(
        f"/api/v1/crowd/zones/{KNOWN_ZONE_SLUG}/readings",
        json=_reading_payload(headcount=12345),
        headers=admin_headers,
    )
    assert response.status_code == 422


def test_create_reading_for_unknown_zone_is_404(
    client: TestClient, admin_headers: dict
):
    response = client.post(
        "/api/v1/crowd/zones/not-a-real-zone/readings",
        json=_reading_payload(),
        headers=admin_headers,
    )
    assert response.status_code == 404
