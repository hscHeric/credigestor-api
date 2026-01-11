from unittest.mock import MagicMock
from app.models.user import User
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

def test_hash_password_integrity():
    pwd = "senha"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True

def test_create_token_default_expiry():
    token = create_access_token(subject="sub", role="admin")
    payload = decode_access_token(token)
    assert payload["sub"] == "sub"
    assert "exp" in payload

def test_create_token_custom_expiry():
    token = create_access_token(subject="sub", role="seller", expires_hours=1)
    payload = decode_access_token(token)
    assert payload["sub"] == "sub"
    assert payload["role"] == "seller"

def test_decode_invalid_token():
    assert decode_access_token("invalid.token") is None

def test_authenticate_user_success():
    mock_db = MagicMock()
    real_hash = hash_password("123")
    fake_user = User(email="a@a.com", password_hash=real_hash)
    
    mock_db.query.return_value.filter.return_value.first.return_value = fake_user

    user = authenticate_user(mock_db, "a@a.com", "123")
    assert user is not None
    assert user.email == "a@a.com"

def test_authenticate_user_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    assert authenticate_user(mock_db, "x", "x") is None

def test_authenticate_user_wrong_password():
    mock_db = MagicMock()
    real_hash = hash_password("senha_correta")
    fake_user = User(email="a@a.com", password_hash=real_hash)
    
    mock_db.query.return_value.filter.return_value.first.return_value = fake_user

    # Passa senha errada
    result = authenticate_user(mock_db, "a@a.com", "senha_errada")
    assert result is None