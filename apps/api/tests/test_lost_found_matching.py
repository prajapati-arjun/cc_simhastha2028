"""
Lost & Found candidate-matching tests (PRD section 16).

The matcher in app/services/lost_found_matching.py is a heuristic, not ML -
these tests assert the ranking signal (same category + overlapping
description words + close report dates ranks a good pair above an unrelated
one) and that two cases are only ever linked through the admin's explicit
POST .../confirm-match call, never automatically by the scorer.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient


def _report(client: TestClient, report_type: str, **overrides) -> str:
    payload = {
        "report_type": report_type,
        "category": "bag",
        "description": (
            "Black leather backpack with a distinctive blue keychain tag, "
            "lost near Ram Ghat"
        ),
        "reporter_phone": "9990000001",
        "occurred_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
    }
    payload.update(overrides)
    response = client.post("/api/v1/lost-found", json=payload)
    assert response.status_code == 201, response.text
    return response.json()["case_reference"]


def _admin_id_for(client: TestClient, admin_headers, case_reference: str) -> int:
    rows = client.get("/api/v1/admin/lost-found", headers=admin_headers).json()["items"]
    return next(r["id"] for r in rows if r["case_reference"] == case_reference)


def _advance_to_verified(client: TestClient, admin_headers, item_id: int) -> None:
    resp1 = client.patch(
        f"/api/v1/admin/lost-found/{item_id}",
        json={"status": "under_review"},
        headers=admin_headers,
    )
    assert resp1.status_code == 200, resp1.text
    resp2 = client.patch(
        f"/api/v1/admin/lost-found/{item_id}",
        json={"status": "verified"},
        headers=admin_headers,
    )
    assert resp2.status_code == 200, resp2.text


def test_candidate_matches_ranks_the_similar_opposite_type_case_first(
    client: TestClient, admin_headers
):
    lost_ref = _report(client, "lost")
    found_ref = _report(
        client,
        "found",
        description=(
            "Found a black backpack with a blue keychain near the ghat steps"
        ),
    )
    unrelated_ref = _report(
        client,
        "found",
        category="documents",
        description="Found a folder of exam papers, no bag at all",
        occurred_at=(datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
    )

    lost_id = _admin_id_for(client, admin_headers, lost_ref)
    found_id = _admin_id_for(client, admin_headers, found_ref)
    unrelated_id = _admin_id_for(client, admin_headers, unrelated_ref)

    response = client.get(
        f"/api/v1/lost-found/{lost_id}/candidate-matches", headers=admin_headers
    )
    assert response.status_code == 200, response.text
    candidates = response.json()
    candidate_ids = [c["id"] for c in candidates]

    assert found_id in candidate_ids
    assert unrelated_id not in candidate_ids
    assert candidates[0]["id"] == found_id
    assert candidates[0]["score"] > 0
    assert candidates[0]["reasons"]


def test_candidate_matches_only_surfaces_opposite_report_type(
    client: TestClient, admin_headers
):
    lost_ref = _report(client, "lost")
    other_lost_ref = _report(client, "lost", description="A totally different red umbrella")
    lost_id = _admin_id_for(client, admin_headers, lost_ref)
    other_lost_id = _admin_id_for(client, admin_headers, other_lost_ref)

    response = client.get(
        f"/api/v1/lost-found/{lost_id}/candidate-matches", headers=admin_headers
    )
    ids = [c["id"] for c in response.json()]
    assert other_lost_id not in ids


def test_candidate_matches_requires_admin(client: TestClient, public_user_token: str):
    response = client.get(
        "/api/v1/lost-found/1/candidate-matches",
        headers={"Authorization": f"Bearer {public_user_token}"},
    )
    assert response.status_code == 403


def test_candidate_matches_unauthenticated_is_401(client: TestClient):
    assert client.get("/api/v1/lost-found/1/candidate-matches").status_code == 401


def test_candidate_matches_missing_case_is_404(client: TestClient, admin_headers):
    response = client.get(
        "/api/v1/lost-found/999999/candidate-matches", headers=admin_headers
    )
    assert response.status_code == 404


def test_confirm_match_requires_both_cases_verified(client: TestClient, admin_headers):
    lost_ref = _report(client, "lost")
    found_ref = _report(
        client, "found", description="Found a black backpack with a blue keychain"
    )
    lost_id = _admin_id_for(client, admin_headers, lost_ref)
    found_id = _admin_id_for(client, admin_headers, found_ref)

    # Neither case has been verified yet - the shared transition table must
    # reject this the same way it rejects any other illegal status jump.
    response = client.post(
        f"/api/v1/lost-found/{lost_id}/confirm-match",
        json={"matched_case_id": found_id},
        headers=admin_headers,
    )
    assert response.status_code == 409


def test_confirm_match_links_both_cases_and_sets_matched_status(
    client: TestClient, admin_headers
):
    lost_ref = _report(client, "lost")
    found_ref = _report(
        client, "found", description="Found a black backpack with a blue keychain"
    )
    lost_id = _admin_id_for(client, admin_headers, lost_ref)
    found_id = _admin_id_for(client, admin_headers, found_ref)

    _advance_to_verified(client, admin_headers, lost_id)
    _advance_to_verified(client, admin_headers, found_id)

    response = client.post(
        f"/api/v1/lost-found/{lost_id}/confirm-match",
        json={"matched_case_id": found_id},
        headers=admin_headers,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "matched"
    assert body["matched_case_id"] == found_id

    rows = client.get("/api/v1/admin/lost-found", headers=admin_headers).json()["items"]
    found_row = next(r for r in rows if r["id"] == found_id)
    assert found_row["status"] == "matched"
    assert found_row["matched_case_id"] == lost_id


def test_confirm_match_rejects_same_report_type(client: TestClient, admin_headers):
    lost_a_ref = _report(client, "lost")
    lost_b_ref = _report(client, "lost", description="A different lost item, red umbrella")
    lost_a_id = _admin_id_for(client, admin_headers, lost_a_ref)
    lost_b_id = _admin_id_for(client, admin_headers, lost_b_ref)
    _advance_to_verified(client, admin_headers, lost_a_id)
    _advance_to_verified(client, admin_headers, lost_b_id)

    response = client.post(
        f"/api/v1/lost-found/{lost_a_id}/confirm-match",
        json={"matched_case_id": lost_b_id},
        headers=admin_headers,
    )
    assert response.status_code == 422


def test_confirm_match_rejects_self_match(client: TestClient, admin_headers):
    lost_ref = _report(client, "lost")
    lost_id = _admin_id_for(client, admin_headers, lost_ref)
    _advance_to_verified(client, admin_headers, lost_id)

    response = client.post(
        f"/api/v1/lost-found/{lost_id}/confirm-match",
        json={"matched_case_id": lost_id},
        headers=admin_headers,
    )
    assert response.status_code == 422


def test_confirm_match_missing_matched_case_is_404(client: TestClient, admin_headers):
    lost_ref = _report(client, "lost")
    lost_id = _admin_id_for(client, admin_headers, lost_ref)
    _advance_to_verified(client, admin_headers, lost_id)

    response = client.post(
        f"/api/v1/lost-found/{lost_id}/confirm-match",
        json={"matched_case_id": 999999},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_confirm_match_requires_admin(client: TestClient, public_user_token: str):
    response = client.post(
        "/api/v1/lost-found/1/confirm-match",
        json={"matched_case_id": 2},
        headers={"Authorization": f"Bearer {public_user_token}"},
    )
    assert response.status_code == 403


def test_unmatched_case_reports_matched_case_id_as_null(client: TestClient, admin_headers):
    lost_ref = _report(client, "lost")
    lost_id = _admin_id_for(client, admin_headers, lost_ref)
    rows = client.get("/api/v1/admin/lost-found", headers=admin_headers).json()["items"]
    row = next(r for r in rows if r["id"] == lost_id)
    assert row["matched_case_id"] is None
