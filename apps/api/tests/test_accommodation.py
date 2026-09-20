"""
Accommodation & essential services API (PRD section 17, roadmap item 2.5).

See the module docstring in test_parking.py for why this suite mounts its
own minimal FastAPI app instead of importing the shared app.main app:
``app/main.py`` is a protected file this sprint (four agents editing the
codebase in parallel), so ``accommodation.router`` is not yet mounted on the
real app. Pasting this agent's ``app.include_router`` snippet into main.py
later makes these same objects work under the real ``client`` fixture too.
"""
from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.v1 import accommodation
from app.db.session import get_db
from app.models.accommodation import Accommodation, EssentialService
from app.schemas.accommodation import AccommodationCreate, EssentialServiceCreate

API_PREFIX = "/api/v1"


@pytest.fixture()
def accommodation_client(db: Session) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(accommodation.router, prefix=API_PREFIX)

    def _override_get_db() -> Iterator[Session]:
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _make_accommodation(db: Session, **overrides) -> Accommodation:
    defaults = dict(
        slug="shipra-dharamshala",
        name="Shipra Dharamshala",
        accommodation_type="dharamshala",
        price_tier="budget",
        verified=False,
        status="published",
        data_source="cms",
    )
    defaults.update(overrides)
    row = Accommodation(**defaults)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _make_service(db: Session, **overrides) -> EssentialService:
    defaults = dict(
        slug="ram-ghat-water-point",
        name="Ram Ghat Drinking Water Point",
        category="drinking_water",
        verified=False,
        status="published",
        data_source="cms",
    )
    defaults.update(overrides)
    row = EssentialService(**defaults)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# --------------------------------------------------------------------------
# Accommodation
# --------------------------------------------------------------------------
def test_accommodation_list_shape(accommodation_client: TestClient, db: Session):
    _make_accommodation(db)
    body = accommodation_client.get(f"{API_PREFIX}/accommodation").json()
    assert set(body) == {"items", "total", "last_updated"}
    assert any(item["slug"] == "shipra-dharamshala" for item in body["items"])


def test_draft_accommodation_is_not_publicly_visible(
    accommodation_client: TestClient, db: Session
):
    _make_accommodation(db, slug="draft-hotel", name="Draft Hotel", status="draft")
    body = accommodation_client.get(f"{API_PREFIX}/accommodation").json()
    assert "draft-hotel" not in {item["slug"] for item in body["items"]}
    assert accommodation_client.get(f"{API_PREFIX}/accommodation/draft-hotel").status_code == 404


def test_filter_by_accommodation_type(accommodation_client: TestClient, db: Session):
    _make_accommodation(db, slug="test-hotel", name="Test Hotel", accommodation_type="hotel")
    _make_accommodation(db, slug="test-ashram", name="Test Ashram", accommodation_type="ashram")

    body = accommodation_client.get(
        f"{API_PREFIX}/accommodation", params={"accommodation_type": "hotel"}
    ).json()
    assert {item["accommodation_type"] for item in body["items"]} == {"hotel"}


def test_unknown_accommodation_type_is_422(accommodation_client: TestClient):
    response = accommodation_client.get(
        f"{API_PREFIX}/accommodation", params={"accommodation_type": "spaceship"}
    )
    assert response.status_code == 422


def test_verified_filter_distinguishes_official_from_third_party(
    accommodation_client: TestClient, db: Session
):
    """PRD section 17's explicit requirement: verified vs third-party/commercial."""
    _make_accommodation(db, slug="verified-stay", name="Verified Stay", verified=True)
    _make_accommodation(db, slug="unverified-stay", name="Unverified Stay", verified=False)

    all_body = accommodation_client.get(f"{API_PREFIX}/accommodation").json()
    slugs = {item["slug"] for item in all_body["items"]}
    assert {"verified-stay", "unverified-stay"} <= slugs
    unverified_item = next(i for i in all_body["items"] if i["slug"] == "unverified-stay")
    assert unverified_item["verified"] is False

    verified_only = accommodation_client.get(
        f"{API_PREFIX}/accommodation", params={"verified": "true"}
    ).json()
    verified_slugs = {item["slug"] for item in verified_only["items"]}
    assert "verified-stay" in verified_slugs
    assert "unverified-stay" not in verified_slugs


def test_accommodation_detail_resolves_by_id_and_by_slug(
    accommodation_client: TestClient, db: Session
):
    row = _make_accommodation(db)
    by_id = accommodation_client.get(f"{API_PREFIX}/accommodation/{row.id}")
    by_slug = accommodation_client.get(f"{API_PREFIX}/accommodation/{row.slug}")
    assert by_id.status_code == by_slug.status_code == 200
    assert by_id.json()["id"] == by_slug.json()["id"] == row.id


def test_unknown_accommodation_ref_is_404(accommodation_client: TestClient):
    assert accommodation_client.get(f"{API_PREFIX}/accommodation/not-real").status_code == 404


# --------------------------------------------------------------------------
# Essential services
# --------------------------------------------------------------------------
def test_essential_services_list_and_filter(accommodation_client: TestClient, db: Session):
    _make_service(db)
    _make_service(db, slug="bhandara-1", name="Community Bhandara", category="bhandara")

    body = accommodation_client.get(f"{API_PREFIX}/accommodation/services").json()
    assert set(body) == {"items", "total", "last_updated"}
    slugs = {item["slug"] for item in body["items"]}
    assert {"ram-ghat-water-point", "bhandara-1"} <= slugs

    filtered = accommodation_client.get(
        f"{API_PREFIX}/accommodation/services", params={"category": "bhandara"}
    ).json()
    assert {item["category"] for item in filtered["items"]} == {"bhandara"}


def test_essential_service_detail_resolves_by_id_and_by_slug(
    accommodation_client: TestClient, db: Session
):
    row = _make_service(db)
    by_id = accommodation_client.get(f"{API_PREFIX}/accommodation/services/{row.id}")
    by_slug = accommodation_client.get(f"{API_PREFIX}/accommodation/services/{row.slug}")
    assert by_id.status_code == by_slug.status_code == 200
    assert by_id.json()["id"] == by_slug.json()["id"] == row.id


def test_draft_essential_service_is_not_publicly_visible(
    accommodation_client: TestClient, db: Session
):
    _make_service(db, slug="draft-toilet", name="Draft Toilet", status="draft")
    body = accommodation_client.get(f"{API_PREFIX}/accommodation/services").json()
    assert "draft-toilet" not in {item["slug"] for item in body["items"]}


def test_unknown_essential_service_ref_is_404(accommodation_client: TestClient):
    assert (
        accommodation_client.get(f"{API_PREFIX}/accommodation/services/not-real").status_code
        == 404
    )


def test_services_literal_route_is_not_swallowed_by_the_ref_route(
    accommodation_client: TestClient, db: Session
):
    """
    Regression guard for route-declaration order: '/accommodation/services'
    must hit the essential-services list, never be treated as
    '/accommodation/{accommodation_ref}' with accommodation_ref='services'.
    """
    _make_service(db)
    response = accommodation_client.get(f"{API_PREFIX}/accommodation/services")
    assert response.status_code == 200
    assert "items" in response.json()


# --------------------------------------------------------------------------
# Schema validation (no admin write endpoint is mounted this sprint - see the
# module docstring - so create/update validation is exercised directly).
# --------------------------------------------------------------------------
def test_accommodation_create_schema_rejects_unknown_type():
    with pytest.raises(ValidationError):
        AccommodationCreate(slug="x", name="X", accommodation_type="spaceship")


def test_essential_service_create_schema_rejects_unknown_category():
    with pytest.raises(ValidationError):
        EssentialServiceCreate(slug="x", name="X", category="fireworks")


def test_accommodation_create_schema_forbids_unexpected_fields():
    with pytest.raises(ValidationError):
        AccommodationCreate(
            slug="x",
            name="X",
            accommodation_type="hotel",
            reporter_name="should not exist",
        )
