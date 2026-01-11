import pytest
from unittest.mock import MagicMock
from app.services.user_service import create_user, list_users, update_user, deactivate_user
from app.schemas.user_schema import UserCreate, UserUpdate
from app.models.user import User

def test_create_user_success():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    data = UserCreate(name="New", email="new@test.com", role="admin", active=True)
    user = create_user(mock_db, data)
    
    assert user.email == "new@test.com"
    assert user.role == "admin"
    mock_db.add.assert_called()

def test_create_user_duplicate_email():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = User()
    
    data = UserCreate(name="Dup", email="dup@test.com", role="seller")
    
    with pytest.raises(ValueError, match="MSG20"):
        create_user(mock_db, data)

def test_list_users():
    mock_db = MagicMock()
    mock_db.query.return_value.order_by.return_value.all.return_value = [User(), User()]
    res = list_users(mock_db)
    assert len(res) == 2

def test_update_user_success():
    mock_db = MagicMock()
    existing = User(id=1, name="Old", email="old@test.com")
    mock_db.query.return_value.filter.return_value.first.return_value = existing
    
    data = UserUpdate(name="Updated", reset_password_to_email=True)
    updated = update_user(mock_db, 1, data)
    
    assert updated.name == "Updated"
    assert updated.password_hash is not None
    mock_db.commit.assert_called()

def test_update_user_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    data = UserUpdate(name="Fantasma")
    
    with pytest.raises(ValueError, match="Usuário não encontrado"):
        update_user(mock_db, 999, data)

def test_deactivate_user_success():
    mock_db = MagicMock()
    u = User(id=1, active=True)
    mock_db.query.return_value.filter.return_value.first.return_value = u
    
    deactivate_user(mock_db, 1)
    assert u.active is False

def test_deactivate_user_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(ValueError, match="Usuário não encontrado"):
        deactivate_user(mock_db, 999)