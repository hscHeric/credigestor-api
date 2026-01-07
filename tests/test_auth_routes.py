from __future__ import annotations

from app.models.user import User, UserRole
from app.services.auth_service import create_access_token, hash_password
from app.services.auth_service import jwt, settings


def _create_user(
    db_session, *, email: str, password: str, role: str, active: bool = True
):
    u = User(
        name="Teste",
        email=email,
        password_hash=hash_password(password),
        role=role,
        active=active,
        temporary_password=False,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


def test_login_success(client, db_session):
    u = _create_user(
        db_session,
        email="admin1@credigestor.com",
        password="admin_credigestor",
        role=UserRole.ADMIN.value,
        active=True,
    )

    r = client.post(
        "/api/auth/login",
        json={"email": "admin1@credigestor.com", "password": "admin_credigestor"},
    )
    assert r.status_code == 200

    body = r.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert "MSG01" in body["message"]
    assert body["user_id"] == u.id
    assert body["user_role"] == "admin"


def test_login_invalid_credentials(client, db_session):
    _create_user(
        db_session,
        email="user1@credigestor.com",
        password="certa",
        role=UserRole.SELLER.value,
        active=True,
    )

    r = client.post(
        "/api/auth/login",
        json={"email": "user1@credigestor.com", "password": "errada"},
    )
    assert r.status_code == 401
    assert "MSG02" in r.json()["detail"]


def test_login_inactive_user(client, db_session):
    _create_user(
        db_session,
        email="inactive1@credigestor.com",
        password="senha",
        role=UserRole.SELLER.value,
        active=False,
    )

    r = client.post(
        "/api/auth/login",
        json={"email": "inactive1@credigestor.com", "password": "senha"},
    )
    assert r.status_code == 403
    assert "MSG04" in r.json()["detail"]


def test_login_empty_fields_hits_msg03(client):
    r = client.post("/api/auth/login", json={"email": "", "password": ""})
    # no router você lança 422 com MSG03
    assert r.status_code == 422
    assert "MSG03" in r.json()["detail"]


def test_me_success(client, db_session):
    u = _create_user(
        db_session,
        email="admin2@credigestor.com",
        password="admin_credigestor",
        role=UserRole.ADMIN.value,
        active=True,
    )

    login = client.post(
        "/api/auth/login",
        json={"email": "admin2@credigestor.com", "password": "admin_credigestor"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()

    assert body["id"] == u.id
    assert body["email"] == "admin2@credigestor.com"
    assert body["role"] == "admin"


def test_me_invalid_token(client):
    r = client.get("/api/auth/me", headers={"Authorization": "Bearer token-invalido"})
    assert r.status_code == 401


def test_me_token_missing_sub_or_role(client):
    payload = {"exp": 9999999999}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401
    assert "Token inválido" in r.json()["detail"]


def test_me_user_not_found_returns_401(client):
    token = create_access_token(subject="999999", role="admin", expires_hours=1)
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401
