"""
Privacy guarantees for missing-person reports (decision D-01, PRD section 31).

This module is the enforcement mechanism for the single strictest rule in the
service: the public read endpoint returns case status and timestamps ONLY.

Why this is worth a dedicated test module rather than one assertion: at an
event serving millions of pilgrims, most missing-person reports concern
children. A response that echoed the child's name, age, photo URL and last-seen
location to anyone holding (or guessing) a case reference would be a serious
privacy failure, and the kind of regression that arrives quietly - somebody
"improves" the status page by returning the whole row.

The tests therefore check three independent layers:
  1. the declared Pydantic response model's field set,
  2. the actual JSON bytes returned by the live endpoint, and
  3. the absence of any enumeration or search surface.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.cases import MissingPersonCase
from app.schemas.cases import MissingPersonPublicOut

#: Distinctive values so a leak is unambiguous when searching the raw response.
PERSON_NAME = "Zzyxtest Kumarvani"
PHYSICAL_DESCRIPTION = "Wearing a qqzz-marked yellow shirt"
LAST_SEEN_LOCATION = "Near Mahakaleshwar gate 2, xyzzy landmark"
PHOTO_URL = "https://example.invalid/qqzz-photo.jpg"
REPORTER_NAME = "Wwvvtest Reporter"
REPORTER_PHONE = "+91-00000-07777"

#: Every field on MissingPersonCase that constitutes personal data.
FORBIDDEN_PUBLIC_FIELDS = {
    "person_name",
    "person_age",
    "person_gender",
    "physical_description",
    "last_seen_location_text",
    "last_seen_at",
    "photo_url",
    "reporter_name",
    "reporter_phone",
    "reporter_relationship",
    "latitude",
    "longitude",
    "admin_notes",
    "id",
}


def _payload(**overrides) -> dict:
    payload = {
        "person_name": PERSON_NAME,
        "person_age": 8,
        "person_gender": "male",
        "physical_description": PHYSICAL_DESCRIPTION,
        "last_seen_location_text": LAST_SEEN_LOCATION,
        "latitude": 23.1828,
        "longitude": 75.7682,
        "last_seen_at": "2026-09-20T08:30:00Z",
        "photo_url": PHOTO_URL,
        "reporter_name": REPORTER_NAME,
        "reporter_phone": REPORTER_PHONE,
        "reporter_relationship": "parent",
        "consent_given": True,
    }
    payload.update(overrides)
    return payload


@pytest.fixture()
def submitted_case(client: TestClient) -> dict:
    response = client.post("/api/v1/missing-person", json=_payload())
    assert response.status_code == 201, response.text
    return response.json()


# --------------------------------------------------------------------------
# Layer 1: the response model itself
# --------------------------------------------------------------------------
def test_public_response_model_declares_only_safe_fields():
    """
    Guards against a personal field being added to MissingPersonPublicOut.

    This fails at the schema level, before any request is made, so the mistake
    is caught even if no route happens to populate the new field yet.
    """
    assert set(MissingPersonPublicOut.model_fields) == {
        "case_reference",
        "status",
        "created_at",
        "updated_at",
        "prototype_notice",
    }
    assert not (
        set(MissingPersonPublicOut.model_fields) & FORBIDDEN_PUBLIC_FIELDS
    )


# --------------------------------------------------------------------------
# Layer 2: the bytes on the wire
# --------------------------------------------------------------------------
def test_public_read_returns_status_and_timestamps_only(
    client: TestClient, submitted_case: dict
):
    response = client.get(f"/api/v1/missing-person/{submitted_case['case_reference']}")
    assert response.status_code == 200
    body = response.json()

    assert set(body) == {
        "case_reference",
        "status",
        "created_at",
        "updated_at",
        "prototype_notice",
    }
    assert body["status"] == "submitted"
    assert body["case_reference"] == submitted_case["case_reference"]


def test_public_read_leaks_no_personal_field_name(
    client: TestClient, submitted_case: dict
):
    body = client.get(
        f"/api/v1/missing-person/{submitted_case['case_reference']}"
    ).json()
    for field in FORBIDDEN_PUBLIC_FIELDS:
        assert field not in body, f"public response leaked field '{field}'"


def test_public_read_leaks_no_personal_value_in_raw_json(
    client: TestClient, submitted_case: dict
):
    """
    Search the raw response text, not the parsed keys.

    A nested object or a renamed field would still slip past a key-only check;
    the submitted values themselves must simply not be present anywhere.
    """
    raw = client.get(
        f"/api/v1/missing-person/{submitted_case['case_reference']}"
    ).text
    for value in (
        PERSON_NAME,
        "Zzyxtest",
        PHYSICAL_DESCRIPTION,
        "qqzz",
        LAST_SEEN_LOCATION,
        "xyzzy",
        PHOTO_URL,
        REPORTER_NAME,
        REPORTER_PHONE,
        "parent",
        "23.1828",
        "75.7682",
    ):
        assert value not in raw, f"public response leaked the value '{value}'"


def test_post_response_also_withholds_personal_data(submitted_case: dict):
    """The 201 body is a second potential leak path - check it too."""
    assert set(submitted_case) == {
        "case_reference",
        "status",
        "created_at",
        "prototype_notice",
    }
    assert PERSON_NAME not in str(submitted_case)


def test_public_read_carries_the_prototype_notice(
    client: TestClient, submitted_case: dict
):
    body = client.get(
        f"/api/v1/missing-person/{submitted_case['case_reference']}"
    ).json()
    assert "NOT automatically sent to police" in body["prototype_notice"]


# --------------------------------------------------------------------------
# Layer 3: no enumeration surface
# --------------------------------------------------------------------------
def test_there_is_no_public_list_endpoint(client: TestClient):
    """A list endpoint here would be a scraping surface over children's data."""
    response = client.get("/api/v1/missing-person")
    assert response.status_code in {404, 405}, response.text


def test_no_public_route_allows_lookup_by_name_or_phone(client: TestClient):
    schema = client.get("/openapi.json").json()
    public_paths = [
        path
        for path in schema["paths"]
        if path.startswith("/api/v1/missing-person")
    ]
    # Exactly two: POST the report, GET it back by opaque reference.
    assert sorted(public_paths) == [
        "/api/v1/missing-person",
        "/api/v1/missing-person/{case_reference}",
    ]

    get_op = schema["paths"]["/api/v1/missing-person/{case_reference}"]["get"]
    param_names = {p["name"] for p in get_op.get("parameters", [])}
    assert param_names == {"case_reference"}


def test_case_references_are_random_unique_and_unambiguous(
    client: TestClient, db: Session
):
    references = [
        client.post("/api/v1/missing-person", json=_payload()).json()["case_reference"]
        for _ in range(5)
    ]
    assert len(set(references)) == 5

    rows = db.execute(
        select(MissingPersonCase).where(
            MissingPersonCase.case_reference.in_(references)
        )
    ).scalars().all()
    for row in rows:
        body = row.case_reference.split("-", 1)[1]
        # A random base-31 reference can naturally contain a digit that also
        # appears in the database id.  Treating that coincidence as evidence
        # of encoding made this privacy test flaky.  Uniqueness and the fixed
        # opaque-reference shape are the observable contract; the generator's
        # CSPRNG implementation is covered in app.core.security.
        # Unambiguous alphabet: no 0/O, no 1/I/L (decision D-01).
        assert not set(body) & set("01OIL")
        assert len(body) == 8


def test_unknown_case_reference_is_404(client: TestClient):
    assert client.get("/api/v1/missing-person/MP-ZZZZZZZZ").status_code == 404


def test_lookup_does_not_fall_back_to_a_numeric_id(
    client: TestClient, submitted_case: dict, db: Session
):
    """Passing the row id must not resolve the case."""
    row = db.execute(
        select(MissingPersonCase).where(
            MissingPersonCase.case_reference == submitted_case["case_reference"]
        )
    ).scalar_one()
    assert client.get(f"/api/v1/missing-person/{row.id}").status_code == 404


# --------------------------------------------------------------------------
# Validation and audit
# --------------------------------------------------------------------------
def test_consent_is_mandatory(client: TestClient):
    assert (
        client.post(
            "/api/v1/missing-person", json=_payload(consent_given=False)
        ).status_code
        == 422
    )
    payload = _payload()
    del payload["consent_given"]
    assert client.post("/api/v1/missing-person", json=payload).status_code == 422


def test_person_name_and_reporter_phone_are_required(client: TestClient):
    assert (
        client.post("/api/v1/missing-person", json=_payload(person_name="")).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/missing-person", json=_payload(reporter_phone="   ")
        ).status_code
        == 422
    )


def test_person_age_must_be_plausible(client: TestClient):
    assert (
        client.post("/api/v1/missing-person", json=_payload(person_age=-1)).status_code
        == 422
    )
    assert (
        client.post("/api/v1/missing-person", json=_payload(person_age=150)).status_code
        == 422
    )


def test_last_seen_at_cannot_be_in_the_future(client: TestClient):
    future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    response = client.post("/api/v1/missing-person", json=_payload(last_seen_at=future))
    assert response.status_code == 422
    assert "future" in response.text


def test_audit_row_records_the_case_but_not_the_person(
    client: TestClient, db: Session, submitted_case: dict
):
    entry = db.execute(
        select(AuditLog).where(
            AuditLog.action == "missing_person.submitted",
            AuditLog.detail["case_reference"].astext
            == submitted_case["case_reference"],
        )
    ).scalar_one()

    assert entry.actor_user_id is None
    assert entry.detail["status"] == "submitted"
    # PRD section 31: the audit trail answers "who did what, when" - it is not
    # a second copy of the child's personal data.
    assert PERSON_NAME not in str(entry.detail)
    assert REPORTER_PHONE not in str(entry.detail)
