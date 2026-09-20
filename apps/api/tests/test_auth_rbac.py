"""Authentication and role-based access control (PRD section 29)."""
from __future__ import annotations

from fastapi.testclient import TestClient
from jose import jwt

from app.core.config import settings

ADMIN_ENDPOINTS = [
    ("GET", "/api/v1/admin/events"),
    ("GET", "/api/v1/admin/announcements"),
    ("GET", "/api/v1/admin/temples"),
    ("GET", "/api/v1/admin/ghats"),
    ("GET", "/api/v1/admin/lost-found"),
    ("GET", "/api/v1/admin/missing-person"),
    ("GET", "/api/v1/admin/dashboard"),
]


def test_login_returns_a_token_and_the_user(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": settings.SEED_SUPER_ADMIN_USERNAME,
            "password": settings.SEED_SUPER_ADMIN_PASSWORD,
        },
    )
    assert response.status_code == 200
    body = response.json()

    assert body["token_type"] == "bearer"
    assert body["expires_in"] > 0
    assert body["user"]["username"] == settings.SEED_SUPER_ADMIN_USERNAME
    assert body["user"]["role"] == "super_admin"


def test_login_never_returns_a_password(client: TestClient):
    raw = client.post(
        "/api/v1/auth/login",
        json={
            "username": settings.SEED_SUPER_ADMIN_USERNAME,
            "password": settings.SEED_SUPER_ADMIN_PASSWORD,
        },
    ).text
    assert "hashed_password" not in raw
    assert settings.SEED_SUPER_ADMIN_PASSWORD not in raw
    assert "$2b$" not in raw  # no bcrypt digest leaked either


def test_token_claims_carry_subject_role_and_expiry(super_admin_token: str):
    claims = jwt.decode(
        super_admin_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
    assert claims["role"] == "super_admin"
    assert int(claims["sub"]) > 0
    assert claims["exp"] > claims["iat"]


def test_bad_password_is_401(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": settings.SEED_SUPER_ADMIN_USERNAME, "password": "wrong"},
    )
    assert response.status_code == 401


def test_unknown_user_is_401_with_the_same_message(client: TestClient):
    """
    Identical response for "no such user" and "wrong password", so an
    unauthenticated caller cannot enumerate administrator usernames.
    """
    unknown = client.post(
        "/api/v1/auth/login", json={"username": "nobody", "password": "wrong"}
    )
    wrong_password = client.post(
        "/api/v1/auth/login",
        json={"username": settings.SEED_SUPER_ADMIN_USERNAME, "password": "wrong"},
    )
    assert unknown.status_code == wrong_password.status_code == 401
    assert unknown.json() == wrong_password.json()


def test_login_requires_a_json_body(client: TestClient):
    """The contract is explicit: JSON, not form-encoded."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "x"},
    )
    assert response.status_code == 422


def test_me_returns_the_authenticated_user(client: TestClient, admin_headers: dict):
    body = client.get("/api/v1/auth/me", headers=admin_headers).json()
    assert body["username"] == settings.SEED_SUPER_ADMIN_USERNAME
    assert body["role"] == "super_admin"
    assert "hashed_password" not in body


def test_me_without_a_token_is_401(client: TestClient):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_with_a_garbage_token_is_401(client: TestClient):
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_me_with_a_token_signed_by_another_key_is_401(client: TestClient):
    forged = jwt.encode(
        {"sub": "1", "role": "super_admin", "exp": 9999999999},
        "an-attackers-secret",
        algorithm="HS256",
    )
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {forged}"}
    )
    assert response.status_code == 401


# --------------------------------------------------------------------------
# RBAC
# --------------------------------------------------------------------------
def test_admin_endpoints_reject_anonymous_callers_with_401(client: TestClient):
    for method, path in ADMIN_ENDPOINTS:
        response = client.request(method, path)
        assert response.status_code == 401, f"{method} {path} -> {response.status_code}"


def test_admin_endpoints_reject_public_users_with_403(
    client: TestClient, public_user_token: str
):
    """
    403, not 401: the caller is authenticated but their role has no admin
    access, and the client needs to tell "log in" from "you cannot do this".
    """
    headers = {"Authorization": f"Bearer {public_user_token}"}
    for method, path in ADMIN_ENDPOINTS:
        response = client.request(method, path, headers=headers)
        assert response.status_code == 403, f"{method} {path} -> {response.status_code}"


def test_super_admin_and_content_manager_both_reach_the_admin_api(
    client: TestClient, super_admin_token: str, content_manager_token: str
):
    for token in (super_admin_token, content_manager_token):
        response = client.get(
            "/api/v1/admin/events", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200


def test_public_user_cannot_reach_write_endpoints_either(
    client: TestClient, public_user_token: str
):
    headers = {"Authorization": f"Bearer {public_user_token}"}
    response = client.post(
        "/api/v1/admin/events",
        headers=headers,
        json={
            "slug": "should-not-exist",
            "title": "Nope",
            "category": "cultural",
            "starts_at": "2028-04-10T05:00:00Z",
        },
    )
    assert response.status_code == 403
