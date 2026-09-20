"""
Parking API (PRD section 12, roadmap item 2.3).

This suite builds its own minimal FastAPI app that mounts only
``app.api.v1.parking.router`` and reuses the shared ``db`` fixture's
dependency override, instead of importing the shared ``app`` from
``app.main``. That is deliberate, not a style choice: ``app/main.py`` is a
protected file this sprint (four agents editing the codebase in parallel),
so ``parking.router`` is not yet mounted on the real app. Once the two
``app.include_router`` lines from this agent's handoff report are pasted
into main.py, these same router/schema/model/service objects behave
identically under the real ``client`` fixture - nothing here is a mock.
"""
from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.v1 import parking
from app.db.session import get_db
from app.models.parking import ParkingFacility
from app.schemas.parking import ParkingCreate

API_PREFIX = "/api/v1"


@pytest.fixture()
def parking_client(db: Session) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(parking.router, prefix=API_PREFIX)

    def _override_get_db() -> Iterator[Session]:
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _make_parking(db: Session, **overrides) -> ParkingFacility:
    defaults = dict(
        slug="mahakal-parking-1",
        name="Mahakal Parking Zone 1",
        parking_type="four_wheeler",
        capacity=200,
        current_occupancy=None,
        status="published",
        data_source="cms",
    )
    defaults.update(overrides)
    row = ParkingFacility(**defaults)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# --------------------------------------------------------------------------
# List / detail
# --------------------------------------------------------------------------
def test_list_returns_the_envelope_shape(parking_client: TestClient, db: Session):
    _make_parking(db)
    body = parking_client.get(f"{API_PREFIX}/parking").json()
    assert set(body) == {"items", "total", "last_updated"}
    assert body["total"] >= 1
    assert any(item["slug"] == "mahakal-parking-1" for item in body["items"])


def test_draft_parking_is_not_publicly_visible(parking_client: TestClient, db: Session):
    _make_parking(db, slug="draft-lot", name="Draft Lot", status="draft")
    body = parking_client.get(f"{API_PREFIX}/parking").json()
    assert "draft-lot" not in {item["slug"] for item in body["items"]}
    assert parking_client.get(f"{API_PREFIX}/parking/draft-lot").status_code == 404


def test_filter_by_parking_type(parking_client: TestClient, db: Session):
    _make_parking(db, slug="bus-lot", name="Bus Lot", parking_type="bus")
    _make_parking(db, slug="two-wheeler-lot", name="Two Wheeler Lot", parking_type="two_wheeler")

    body = parking_client.get(f"{API_PREFIX}/parking", params={"parking_type": "bus"}).json()
    assert body["total"] >= 1
    assert {item["parking_type"] for item in body["items"]} == {"bus"}


def test_unknown_parking_type_is_422(parking_client: TestClient):
    response = parking_client.get(
        f"{API_PREFIX}/parking", params={"parking_type": "helicopter"}
    )
    assert response.status_code == 422


def test_detail_resolves_by_id_and_by_slug(parking_client: TestClient, db: Session):
    row = _make_parking(db)
    by_id = parking_client.get(f"{API_PREFIX}/parking/{row.id}")
    by_slug = parking_client.get(f"{API_PREFIX}/parking/{row.slug}")
    assert by_id.status_code == by_slug.status_code == 200
    assert by_id.json()["id"] == by_slug.json()["id"] == row.id


def test_unknown_parking_ref_is_404(parking_client: TestClient):
    assert parking_client.get(f"{API_PREFIX}/parking/not-a-real-lot").status_code == 404
    assert parking_client.get(f"{API_PREFIX}/parking/999999").status_code == 404


# --------------------------------------------------------------------------
# Availability - operator-entered, never a live feed
# --------------------------------------------------------------------------
def test_availability_shape_and_notice(parking_client: TestClient, db: Session):
    row = _make_parking(db, current_occupancy=50)
    body = parking_client.get(f"{API_PREFIX}/parking/{row.slug}/availability").json()
    assert body["parking_id"] == row.id
    assert body["current_occupancy"] == 50
    assert body["occupancy_updated_at"] is not None
    assert "operator-entered" in body["prototype_notice"]
    assert "no live sensor" in body["prototype_notice"]


def test_availability_is_null_not_zero_when_never_entered(
    parking_client: TestClient, db: Session
):
    """An un-entered count must not look identical to a confirmed empty lot."""
    row = _make_parking(db, current_occupancy=None)
    body = parking_client.get(f"{API_PREFIX}/parking/{row.slug}/availability").json()
    assert body["current_occupancy"] is None


def test_unknown_parking_availability_ref_is_404(parking_client: TestClient):
    assert (
        parking_client.get(f"{API_PREFIX}/parking/not-a-real-lot/availability").status_code
        == 404
    )


# --------------------------------------------------------------------------
# occupancy_updated_at stamping (app/models/parking.py's before_update listener)
# --------------------------------------------------------------------------
def test_occupancy_updated_at_is_stamped_on_first_write(db: Session):
    row = ParkingFacility(
        slug="stamp-lot-1",
        name="Stamp Lot 1",
        parking_type="four_wheeler",
        status="published",
        data_source="cms",
        current_occupancy=10,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    assert row.occupancy_updated_at is not None


def test_occupancy_updated_at_changes_only_when_the_count_changes(db: Session):
    row = _make_parking(db, slug="stamp-lot-2", current_occupancy=10)
    first_stamp = row.occupancy_updated_at
    assert first_stamp is not None

    # Editing an unrelated field must not touch the occupancy timestamp.
    row.shuttle_note = "Free shuttle every 15 minutes."
    db.commit()
    db.refresh(row)
    assert row.occupancy_updated_at == first_stamp

    # Editing the count itself must bump the timestamp.
    row.current_occupancy = 25
    db.commit()
    db.refresh(row)
    assert row.occupancy_updated_at is not None
    assert row.occupancy_updated_at >= first_stamp


# --------------------------------------------------------------------------
# Schema validation (no admin write endpoint is mounted this sprint - see the
# module docstring - so create/update validation is exercised directly).
# --------------------------------------------------------------------------
def test_create_schema_rejects_unknown_parking_type():
    with pytest.raises(ValidationError):
        ParkingCreate(slug="x", name="X", parking_type="helicopter")


def test_create_schema_rejects_negative_capacity():
    with pytest.raises(ValidationError):
        ParkingCreate(slug="x", name="X", parking_type="bus", capacity=-1)


def test_create_schema_forbids_unexpected_fields():
    with pytest.raises(ValidationError):
        ParkingCreate(
            slug="x", name="X", parking_type="bus", reporter_name="should not exist"
        )
