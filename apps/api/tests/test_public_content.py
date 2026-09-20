"""Public read APIs: events, temples, ghats, announcements."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.models.enums import ContentStatus

REQUIRED_TEMPLE_SLUGS = {
    "mahakaleshwar",
    "kal-bhairav",
    "harsiddhi",
    "mangalnath",
    "gadkalika",
    "chintaman-ganesh",
    "sandipani-ashram",
    "84-mahadev",
    "panchkroshi-yatra",
}

ENVELOPE_KEYS = {"items", "total", "last_updated"}


# --------------------------------------------------------------------------
# Envelope conventions (contract section 0)
# --------------------------------------------------------------------------
def test_list_endpoints_share_the_envelope_shape(client: TestClient):
    for path in (
        "/api/v1/events",
        "/api/v1/temples",
        "/api/v1/ghats",
        "/api/v1/emergency/services",
        "/api/v1/announcements",
    ):
        body = client.get(path).json()
        assert set(body) == ENVELOPE_KEYS, path
        assert isinstance(body["items"], list)
        assert isinstance(body["total"], int)


def test_timestamps_are_iso_utc_with_z_suffix(client: TestClient):
    item = client.get("/api/v1/temples").json()["items"][0]
    assert item["updated_at"].endswith("Z")
    assert "+00:00" not in item["updated_at"]


# --------------------------------------------------------------------------
# Temples
# --------------------------------------------------------------------------
def test_temples_returns_the_nine_named_temples(client: TestClient):
    body = client.get("/api/v1/temples").json()
    assert body["total"] == 9
    assert {item["slug"] for item in body["items"]} == REQUIRED_TEMPLE_SLUGS


def test_seeded_temples_are_never_marked_verified(client: TestClient):
    """Nothing in this prototype is authority-verified (contract section 2)."""
    for item in client.get("/api/v1/temples").json()["items"]:
        assert item["verified"] is False, item["slug"]
        assert item["data_source"] == "placeholder", item["slug"]


def test_temple_timings_are_explicitly_placeholder_text(client: TestClient):
    """Invented darshan timings would send pilgrims to a closed temple."""
    for item in client.get("/api/v1/temples").json()["items"]:
        assert "Placeholder" in item["timings"], item["slug"]
        assert "Placeholder" in item["accessibility_info"], item["slug"]


def test_temple_detail_by_slug(client: TestClient):
    body = client.get("/api/v1/temples/mahakaleshwar").json()
    assert body["slug"] == "mahakaleshwar"
    assert body["latitude"] == 23.1828
    assert body["longitude"] == 75.7682
    # Contract section 0: coordinates are plain floats, not GeoJSON.
    assert isinstance(body["latitude"], float)


def test_unknown_temple_slug_is_404(client: TestClient):
    assert client.get("/api/v1/temples/not-a-real-temple").status_code == 404


# --------------------------------------------------------------------------
# Events
# --------------------------------------------------------------------------
def test_events_list_and_detail(client: TestClient):
    body = client.get("/api/v1/events").json()
    assert body["total"] >= 7
    slugs = {item["slug"] for item in body["items"]}
    assert "first-shahi-snan" in slugs

    detail = client.get("/api/v1/events/first-shahi-snan").json()
    assert detail["category"] == "snan_parva"
    assert detail["status"] == ContentStatus.PUBLISHED.value


def test_events_category_filter(client: TestClient):
    body = client.get("/api/v1/events", params={"category": "aarti"}).json()
    assert body["total"] >= 1
    assert {item["category"] for item in body["items"]} == {"aarti"}


def test_events_reject_unknown_category(client: TestClient):
    assert client.get("/api/v1/events", params={"category": "nonsense"}).status_code == 422


def test_events_date_range_filter(client: TestClient):
    body = client.get(
        "/api/v1/events", params={"from_date": "2028-04-09", "to_date": "2028-04-09"}
    ).json()
    assert body["total"] >= 1
    for item in body["items"]:
        assert item["starts_at"].startswith("2028-04-09")


def test_events_pagination_limits(client: TestClient):
    body = client.get("/api/v1/events", params={"limit": 2}).json()
    assert len(body["items"]) == 2
    assert body["total"] >= 7  # total counts all matches, not the page
    assert client.get("/api/v1/events", params={"limit": 0}).status_code == 422


def test_unknown_event_slug_is_404(client: TestClient):
    assert client.get("/api/v1/events/no-such-event").status_code == 404


# --------------------------------------------------------------------------
# Ghats
# --------------------------------------------------------------------------
def test_ghats_list(client: TestClient):
    body = client.get("/api/v1/ghats").json()
    assert body["total"] >= 3
    ram = next(i for i in body["items"] if i["slug"] == "ram-ghat")
    assert isinstance(ram["facilities"], list)
    assert "drinking_water" in ram["facilities"]


def test_ghat_status_resolves_by_numeric_id_and_by_slug(client: TestClient):
    """The contract pins one path for both key types (PRD section 37)."""
    ghat = client.get("/api/v1/ghats").json()["items"][0]

    by_id = client.get(f"/api/v1/ghats/{ghat['id']}/status")
    by_slug = client.get(f"/api/v1/ghats/{ghat['slug']}/status")

    assert by_id.status_code == 200
    assert by_slug.status_code == 200
    assert by_id.json()["ghat_id"] == by_slug.json()["ghat_id"] == ghat["id"]
    assert by_id.json()["slug"] == ghat["slug"]


def test_ghat_status_never_reports_a_crowd_level(client: TestClient):
    """
    No crowd sensor or CCTV feed exists this sprint. A fabricated crowd badge
    on a bathing-ghat page could influence where someone takes a family into a
    river, so the field must stay null and say why.
    """
    body = client.get("/api/v1/ghats/ram-ghat/status").json()
    assert body["crowd_level"] is None
    assert body["status"] in {"open", "restricted", "closed"}
    assert "no live sensor or CCTV feed" in body["prototype_notice"]


def test_unknown_ghat_status_is_404(client: TestClient):
    assert client.get("/api/v1/ghats/not-a-ghat/status").status_code == 404
    assert client.get("/api/v1/ghats/999999/status").status_code == 404


# --------------------------------------------------------------------------
# Announcements
# --------------------------------------------------------------------------
def test_announcements_are_published_and_unexpired(client: TestClient):
    body = client.get("/api/v1/announcements").json()
    assert body["total"] >= 1
    for item in body["items"]:
        assert item["status"] == "published"
        assert item["priority"] in {"normal", "important", "critical"}
