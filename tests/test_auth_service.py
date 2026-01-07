from __future__ import annotations

from app.models.user import User, UserRole
from app.services.auth import (
    authenticate_user,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password():
    hashed = hash_password("minha_senha")
    assert isinstance(hashed, str)
    assert hashed != "minha_senha"

    assert verify_password("minha_senha", hashed) is True
    assert verify_password("errada", hashed) is False


def test_create_and_decode_access_token():
    token = create_access_token(subject="123", role="admin", expires_hours=1)
    payload = decode_access_token(token)

    assert payload is not None
    assert payload.get("sub") == "123"
    assert payload.get("role") == "admin"


def test_decode_access_token_invalid_returns_none():
    assert decode_access_token("token.invalido") is None


def test_authenticate_user_success(db_session):
    user = User(
        name="U",
        email="u1@u.com",
        password_hash=hash_password("senha"),
        role=UserRole.SELLER.value,
        active=True,
        temporary_password=False,
    )
    db_session.add(user)
    db_session.commit()

    found = authenticate_user(db_session, "u1@u.com", "senha")
    assert found is not None
    assert found.email == "u1@u.com"


def test_authenticate_user_wrong_password_returns_none(db_session):
    user = User(
        name="U",
        email="u2@u.com",
        password_hash=hash_password("senha"),
        role=UserRole.SELLER.value,
        active=True,
        temporary_password=False,
    )
    db_session.add(user)
    db_session.commit()

    found = authenticate_user(db_session, "u2@u.com", "outra")
    assert found is None


def test_authenticate_user_not_found_returns_none(db_session):
    found = authenticate_user(db_session, "naoexiste@u.com", "senha")
    assert found is None

