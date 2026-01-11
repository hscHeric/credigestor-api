from unittest.mock import MagicMock
from app.services.system_config_service import get_or_create_system_config
from app.models.system_config import SystemConfig

def test_get_existing_config():
    mock_db = MagicMock()
    existing = SystemConfig(id=1, company_name="Existing")
    mock_db.query.return_value.order_by.return_value.first.return_value = existing

    cfg = get_or_create_system_config(mock_db)
    assert cfg.company_name == "Existing"

def test_create_new_config_if_none():
    mock_db = MagicMock()
    mock_db.query.return_value.order_by.return_value.first.return_value = None

    cfg = get_or_create_system_config(mock_db)
    
    assert isinstance(cfg, SystemConfig)
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()