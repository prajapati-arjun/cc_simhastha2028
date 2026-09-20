"""Lost & Found public API (PRD section 16, decision D-01)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit import AuditLog

REPORTER_NAME = "Qqzztest Reporter"
REPORTER_PHONE = "+91-00000-08888"
DESCRIPTION = "Brown backpack with a blue zip and a xyzzy luggage tag."


def _payload(**overrides) -> dict:
    payload = {
        "report_type": "lost",
        "category": "bag",
        "description": DESCRIPTION,
        "location_text": "Near Ram Ghat gate 3",
        "latitude": None,
        "longitude": None,
        # Keep the ordinary valid-submission fixture independent of the wall
        # clock. A fixed same-day time becomes a future timestamp whenever
        # this suite runs before that hour; the validation test below supplies
        # an explicitly future value when it needs to exercise that branch.
        "occurred_at": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
        "reporter_name": REPORTER_NAME,
        "reporter_phone": REPORTER_PHONE,
        "image_url": None,
    }
    payload.update(overrides)
    return payload


@pytest.fixture()
def submitted_case(client: TestClient) -> dict:
    response = client.post("/api/v1/lost-found", json=_payload())
    assert response.status_code == 201, response.text
    return response.json()


def test_submit_returns_an_opaque_reference(submitted_case: dict):
    assert set(submitted_case) == {
        "case_reference",
        "status",
        "created_at",
        "prototype_notice",
    }
    assert submitted_case["status"] == "submitted"
    assert submitted_case["case_reference"].startswith("LF-")
    assert "not shared with police" in submitted_case["prototype_notice"]


def test_case_reference_uses_the_unambiguous_alphabet(client: TestClient):
    """No 0/O or 1/I/L - references get read aloud and written on paper."""
    references = {
        client.post("/api/v1/lost-found", json=_payload()).json()["case_reference"]
        for _ in range(5)
    }
    assert len(references) == 5, "references are not random"
    for reference in references:
        body = reference.split("-", 1)[1]
        assert len(body) == 8
        assert not set(body) & set("01OIL")


def test_read_back_by_case_reference(client: TestClient, submitted_case: dict):
    body = client.get(f"/api/v1/lost-found/{submitted_case['case_reference']}").json()
    assert body["case_reference"] == submitted_case["case_reference"]
    assert body["report_type"] == "lost"
    assert body["category"] == "bag"
    assert body["status"] == "submitted"


def test_public_read_withholds_reporter_details_and_free_text(
    client: TestClient, submitted_case: dict
):
    """
    A leaked or brute-forced reference should disclose as little as possible,
    so the reporter's name/phone, the description and the image stay private.
    """
    response = client.get(f"/api/v1/lost-found/{submitted_case['case_reference']}")
    assert set(response.json()) == {
        "case_reference",
        "report_type",
        "category",
        "status",
        "created_at",
        "updated_at",
        "prototype_notice",
    }
    raw = response.text
    for value in (REPORTER_NAME, REPORTER_PHONE, DESCRIPTION, "xyzzy", "Qqzztest"):
        assert value not in raw


def test_there_is_no_public_list_endpoint(client: TestClient):
    assert client.get("/api/v1/lost-found").status_code in {404, 405}


def test_unknown_reference_is_404(client: TestClient):
    assert client.get("/api/v1/lost-found/LF-ZZZZZZZZ").status_code == 404


# --------------------------------------------------------------------------
# Validation (contract section 5)
# --------------------------------------------------------------------------
def test_description_must_be_at_least_ten_characters(client: TestClient):
    assert (
        client.post("/api/v1/lost-found", json=_payload(description="short")).status_code
        == 422
    )


def test_description_is_capped_at_two_thousand_characters(client: TestClient):
    assert (
        client.post(
            "/api/v1/lost-found", json=_payload(description="x" * 2001)
        ).status_code
        == 422
    )


def test_reporter_phone_is_required_and_non_empty(client: TestClient):
    payload = _payload()
    del payload["reporter_phone"]
    assert client.post("/api/v1/lost-found", json=payload).status_code == 422
    assert (
        client.post("/api/v1/lost-found", json=_payload(reporter_phone="  ")).status_code
        == 422
    )


def test_occurred_at_cannot_be_in_the_future(client: TestClient):
    future = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    response = client.post("/api/v1/lost-found", json=_payload(occurred_at=future))
    assert response.status_code == 422
    assert "future" in response.text


def test_unknown_enum_values_are_rejected(client: TestClient):
    assert (
        client.post("/api/v1/lost-found", json=_payload(report_type="stolen")).status_code
        == 422
    )
    assert (
        client.post("/api/v1/lost-found", json=_payload(category="spaceship")).status_code
        == 422
    )


def test_unexpected_fields_are_rejected(client: TestClient):
    """extra="forbid" stops a client silently writing a field we do not store."""
    assert (
        client.post(
            "/api/v1/lost-found", json=_payload(is_admin=True)
        ).status_code
        == 422
    )


def test_submission_writes_an_audit_row(
    client: TestClient, db: Session, submitted_case: dict
):
    entry = db.execute(
        select(AuditLog).where(
            AuditLog.action == "lost_found.submitted",
            AuditLog.detail["case_reference"].astext
            == submitted_case["case_reference"],
        )
    ).scalar_one()
    assert entry.actor_user_id is None
    assert entry.detail["category"] == "bag"
    assert REPORTER_PHONE not in str(entry.detail)
