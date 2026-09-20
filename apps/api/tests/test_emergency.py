"""
Emergency directory and the simulated SOS endpoint.

These tests exist as much to police the safety claims as the mechanics: a
regression that seeded a real phone number, or dropped the `simulated` flag,
would be a serious problem rather than a cosmetic one.
"""
from __future__ import annotations

import re

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.emergency import SosIncident

#: Every seeded number must match this deliberately invalid pattern.
PLACEHOLDER_PHONE = re.compile(r"^\+91-00000-000\d{2}$")

#: Numbers that must NEVER appear in the directory.
REAL_EMERGENCY_NUMBERS = {"100", "101", "102", "108", "112", "1091", "1098"}


def test_emergency_services_list(client: TestClient):
    body = client.get("/api/v1/emergency/services").json()
    assert body["total"] >= 8
    categories = {item["category"] for item in body["items"]}
    assert {"police", "ambulance", "fire", "medical"} <= categories


def test_every_seeded_phone_number_is_an_obvious_placeholder(client: TestClient):
    for item in client.get("/api/v1/emergency/services").json()["items"]:
        assert PLACEHOLDER_PHONE.match(item["phone"]), item
        digits = re.sub(r"\D", "", item["phone"])
        assert digits not in REAL_EMERGENCY_NUMBERS


def test_no_real_emergency_number_appears_anywhere_in_the_directory(
    client: TestClient,
):
    """A user must never be able to tap-to-call something this prototype implies is live."""
    raw = client.get("/api/v1/emergency/services").text
    for number in REAL_EMERGENCY_NUMBERS:
        assert f'"phone":"+91-{number}' not in raw
        assert f'"phone":"{number}"' not in raw


def test_every_directory_entry_carries_the_prototype_notice(client: TestClient):
    for item in client.get("/api/v1/emergency/services").json()["items"]:
        assert "not connected to live emergency dispatch" in item["prototype_notice"]
        assert item["data_source"] == "placeholder"


def test_emergency_services_category_filter(client: TestClient):
    body = client.get(
        "/api/v1/emergency/services", params={"category": "police"}
    ).json()
    assert body["total"] >= 1
    assert {item["category"] for item in body["items"]} == {"police"}


def test_emergency_services_reject_unknown_category(client: TestClient):
    response = client.get(
        "/api/v1/emergency/services", params={"category": "coast_guard"}
    )
    assert response.status_code == 422


# --------------------------------------------------------------------------
# SOS - simulated
# --------------------------------------------------------------------------
def _sos_payload(**overrides) -> dict:
    payload = {
        "reporter_name": "Test Reporter",
        "reporter_phone": "+91-00000-09999",
        "situation_category": "medical",
        "note": "Test submission from the automated suite.",
        "latitude": 23.1828,
        "longitude": 75.7682,
        "consent_given": True,
    }
    payload.update(overrides)
    return payload


def test_sos_records_a_simulated_incident(client: TestClient):
    response = client.post("/api/v1/emergency/sos", json=_sos_payload())
    assert response.status_code == 201
    body = response.json()

    assert body["simulated"] is True
    assert body["status"] == "recorded"
    assert body["case_reference"].startswith("SOS-")
    assert "Nothing was dispatched" in body["prototype_notice"]
    assert "no responder was notified" in body["prototype_notice"]


def test_sos_openapi_description_states_it_dispatches_nothing(client: TestClient):
    schema = client.get("/openapi.json").json()
    description = schema["paths"]["/api/v1/emergency/sos"]["post"]["description"]
    assert "dispatches nothing" in description
    assert "prototype" in description.lower()


def test_sos_requires_explicit_consent(client: TestClient):
    assert (
        client.post(
            "/api/v1/emergency/sos", json=_sos_payload(consent_given=False)
        ).status_code
        == 422
    )
    payload = _sos_payload()
    del payload["consent_given"]
    assert client.post("/api/v1/emergency/sos", json=payload).status_code == 422


def test_sos_rejects_unknown_situation_category(client: TestClient):
    response = client.post(
        "/api/v1/emergency/sos", json=_sos_payload(situation_category="alien_invasion")
    )
    assert response.status_code == 422


def test_sos_rejects_out_of_range_coordinates(client: TestClient):
    response = client.post("/api/v1/emergency/sos", json=_sos_payload(latitude=120.0))
    assert response.status_code == 422


def test_sos_persists_the_simulated_flag_in_the_database(
    client: TestClient, db: Session
):
    reference = client.post("/api/v1/emergency/sos", json=_sos_payload()).json()[
        "case_reference"
    ]
    row = db.execute(
        select(SosIncident).where(SosIncident.case_reference == reference)
    ).scalar_one()
    # Stored, not merely rendered: an export of this table can never be
    # mistaken for a log of real dispatches.
    assert row.simulated is True
    assert row.latitude == 23.1828


def test_sos_submission_writes_an_audit_row(client: TestClient, db: Session):
    reference = client.post("/api/v1/emergency/sos", json=_sos_payload()).json()[
        "case_reference"
    ]
    entry = db.execute(
        select(AuditLog).where(
            AuditLog.action == "sos.submitted",
            AuditLog.detail["case_reference"].astext == reference,
        )
    ).scalar_one()
    assert entry.actor_user_id is None  # public, unauthenticated submission
    assert entry.detail["simulated"] is True
    # Data minimisation: the free-text note must not reach the audit trail.
    assert entry.detail.get("note") is None
