"""
Incident management API tests (PRD section 25).

MOUNTING NOTE: app/api/v1/incidents.py is not yet wired into app/main.py -
that file is owned by another workstream during this parallel Phase 3 build
(see the final report for the exact `app.include_router(...)` line to add
there permanently). This module mounts the router onto the shared FastAPI
`app` object that tests/conftest.py's `client` fixture already talks to, so
this feature is independently testable without touching main.py's source.
The guard below makes this import-time side effect idempotent if pytest
collects this module more than once in a session.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.v1 import incidents as incidents_module
from app.main import app
from app.models.incident import Incident

API_V1_PREFIX = "/api/v1"

if not any(getattr(r, "path", "").startswith(f"{API_V1_PREFIX}/incidents") for r in app.routes):
    app.include_router(incidents_module.router, prefix=API_V1_PREFIX)


def _create_payload(**overrides) -> dict:
    payload = {
        "category": "medical",
        "priority": "P1",
        "title": "Fainting reported near Ram Ghat",
        "description": "Pilgrim collapsed, requesting medical attention.",
    }
    payload.update(overrides)
    return payload


def _create(client: TestClient, admin_headers, **overrides) -> dict:
    response = client.post(
        "/api/v1/incidents", json=_create_payload(**overrides), headers=admin_headers
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_incident_starts_reported_with_sla_due_at(client: TestClient, admin_headers):
    body = _create(client, admin_headers)
    assert body["status"] == "reported"
    assert body["escalated"] is False
    assert body["sla_due_at"] is not None
    assert body["resolved_at"] is None
    assert body["simulated"] is True
    assert "Demo prototype" in body["prototype_notice"]


def test_create_incident_defaults_priority_to_p4(client: TestClient, admin_headers):
    payload = _create_payload()
    del payload["priority"]
    response = client.post("/api/v1/incidents", json=payload, headers=admin_headers)
    assert response.status_code == 201, response.text
    assert response.json()["priority"] == "P4"


def test_create_incident_requires_admin(client: TestClient, public_user_token: str):
    response = client.post(
        "/api/v1/incidents",
        json=_create_payload(),
        headers={"Authorization": f"Bearer {public_user_token}"},
    )
    assert response.status_code == 403


def test_create_incident_unauthenticated_is_401(client: TestClient):
    assert client.post("/api/v1/incidents", json=_create_payload()).status_code == 401


def test_unknown_category_is_rejected(client: TestClient, admin_headers):
    response = client.post(
        "/api/v1/incidents", json=_create_payload(category="dragon"), headers=admin_headers
    )
    assert response.status_code == 422


def test_valid_transition_chain_succeeds_and_stamps_resolved_at(
    client: TestClient, admin_headers
):
    created = _create(client, admin_headers)
    item_id = created["id"]

    for target in ["classified", "assigned", "in_response", "resolved", "closed"]:
        response = client.post(
            f"/api/v1/incidents/{item_id}/transition",
            json={"status": target},
            headers=admin_headers,
        )
        assert response.status_code == 200, response.text
        assert response.json()["status"] == target

    final = client.get(f"/api/v1/incidents/{item_id}", headers=admin_headers).json()
    assert final["resolved_at"] is not None


def test_skipping_a_stage_is_rejected(client: TestClient, admin_headers):
    created = _create(client, admin_headers)
    response = client.post(
        f"/api/v1/incidents/{created['id']}/transition",
        json={"status": "assigned"},
        headers=admin_headers,
    )
    assert response.status_code == 409


def test_closed_is_terminal(client: TestClient, admin_headers):
    created = _create(client, admin_headers)
    item_id = created["id"]
    for target in ["classified", "assigned", "in_response", "resolved", "closed"]:
        client.post(
            f"/api/v1/incidents/{item_id}/transition", json={"status": target}, headers=admin_headers
        )
    response = client.post(
        f"/api/v1/incidents/{item_id}/transition", json={"status": "reported"}, headers=admin_headers
    )
    assert response.status_code == 409


def test_status_is_not_writable_via_patch(client: TestClient, admin_headers):
    created = _create(client, admin_headers)
    response = client.patch(
        f"/api/v1/incidents/{created['id']}",
        json={"status": "closed"},
        headers=admin_headers,
    )
    assert response.status_code == 422


def test_patch_updates_department_and_zone(client: TestClient, admin_headers):
    created = _create(client, admin_headers)
    response = client.patch(
        f"/api/v1/incidents/{created['id']}",
        json={"assigned_department": "Medical response unit 3"},
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["assigned_department"] == "Medical response unit 3"


def test_patch_priority_change_rebases_sla_due_at(client: TestClient, admin_headers):
    created = _create(client, admin_headers, priority="P4")
    original_due = created["sla_due_at"]

    response = client.patch(
        f"/api/v1/incidents/{created['id']}",
        json={"priority": "P1"},
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["priority"] == "P1"
    assert body["sla_due_at"] != original_due


def test_list_filters_by_priority(client: TestClient, admin_headers):
    _create(client, admin_headers, category="fire", priority="P2")
    response = client.get("/api/v1/incidents", params={"priority": "P2"}, headers=admin_headers)
    assert response.status_code == 200, response.text
    items = response.json()["items"]
    assert len(items) >= 1
    assert all(item["priority"] == "P2" for item in items)


def test_list_filters_by_status(client: TestClient, admin_headers):
    created = _create(client, admin_headers)
    client.post(
        f"/api/v1/incidents/{created['id']}/transition",
        json={"status": "classified"},
        headers=admin_headers,
    )
    response = client.get("/api/v1/incidents", params={"status": "classified"}, headers=admin_headers)
    assert response.status_code == 200
    ids = [item["id"] for item in response.json()["items"]]
    assert created["id"] in ids


def test_list_requires_admin(client: TestClient, public_user_token: str):
    response = client.get(
        "/api/v1/incidents", headers={"Authorization": f"Bearer {public_user_token}"}
    )
    assert response.status_code == 403


def test_sla_breach_is_flagged_on_next_read(client: TestClient, admin_headers, db):
    created = _create(client, admin_headers, priority="P1")
    row = db.execute(select(Incident).where(Incident.id == created["id"])).scalar_one()
    row.sla_due_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db.commit()

    response = client.get(f"/api/v1/incidents/{created['id']}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["escalated"] is True


def test_resolved_incident_cannot_retroactively_escalate(client: TestClient, admin_headers, db):
    created = _create(client, admin_headers, priority="P4")
    item_id = created["id"]
    for target in ["classified", "assigned", "in_response", "resolved"]:
        client.post(
            f"/api/v1/incidents/{item_id}/transition", json={"status": target}, headers=admin_headers
        )

    row = db.execute(select(Incident).where(Incident.id == item_id)).scalar_one()
    row.sla_due_at = datetime.now(timezone.utc) - timedelta(days=1)
    db.commit()

    response = client.get(f"/api/v1/incidents/{item_id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["escalated"] is False


def test_soft_deleted_incident_is_not_returned(client: TestClient, admin_headers):
    created = _create(client, admin_headers)
    item_id = created["id"]
    assert client.delete(f"/api/v1/incidents/{item_id}", headers=admin_headers).status_code == 204
    assert client.get(f"/api/v1/incidents/{item_id}", headers=admin_headers).status_code == 404


def test_get_missing_incident_is_404(client: TestClient, admin_headers):
    assert client.get("/api/v1/incidents/999999", headers=admin_headers).status_code == 404
