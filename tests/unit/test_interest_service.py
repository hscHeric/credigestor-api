import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.services.interest_service import calculate_interest_and_fine_for_note
from app.models.promissory_note import PromissoryNote, PromissoryNoteStatus
from app.models.system_config import SystemConfig

@pytest.fixture
def mock_config():
    return SystemConfig(
        fine_rate=Decimal("2.00"),
        monthly_interest_rate=Decimal("1.00")
    )

@patch("app.services.interest_service.get_or_create_system_config")
def test_calculate_no_overdue(mock_get_config, mock_config):
    mock_get_config.return_value = mock_config
    mock_db = MagicMock()
    
    note = PromissoryNote(
        original_amount=Decimal("100.00"),
        paid_amount=Decimal("0.00"),
        due_date=date.today(),
        status=PromissoryNoteStatus.PENDING.value
    )

    result = calculate_interest_and_fine_for_note(mock_db, note=note)
    assert result["fine_amount"] == Decimal("0.00")
    assert result["interest_amount"] == Decimal("0.00")

@patch("app.services.interest_service.get_or_create_system_config")
def test_calculate_with_overdue(mock_get_config, mock_config):
    mock_get_config.return_value = mock_config
    mock_db = MagicMock()
    
    note = PromissoryNote(
        original_amount=Decimal("100.00"),
        paid_amount=Decimal("0.00"),
        due_date=date.today() - timedelta(days=30),
        status=PromissoryNoteStatus.PENDING.value
    )

    result = calculate_interest_and_fine_for_note(mock_db, note=note)
    assert result["fine_amount"] == Decimal("2.00")
    assert result["interest_amount"] == Decimal("1.00")
    assert result["total_updated"] == Decimal("103.00")

@patch("app.services.interest_service.get_or_create_system_config")
def test_calculate_partial_paid(mock_get_config, mock_config):
    mock_get_config.return_value = mock_config
    mock_db = MagicMock()

    note = PromissoryNote(
        original_amount=Decimal("200.00"),
        paid_amount=Decimal("100.00"),
        due_date=date.today() - timedelta(days=30),
        status=PromissoryNoteStatus.PARTIAL_PAYMENT.value
    )

    result = calculate_interest_and_fine_for_note(mock_db, note=note)
    assert result["outstanding_balance"] == Decimal("100.00")
    assert result["fine_amount"] == Decimal("2.00")

@patch("app.services.interest_service.get_or_create_system_config")
def test_calculate_already_paid_or_zero_balance(mock_get_config, mock_config):
    mock_get_config.return_value = mock_config
    mock_db = MagicMock()

    note_paid = PromissoryNote(
        original_amount=Decimal("100.00"),
        paid_amount=Decimal("100.00"),
        due_date=date.today() - timedelta(days=10), # Mesmo vencida
        status=PromissoryNoteStatus.PAID.value
    )
    res_paid = calculate_interest_and_fine_for_note(mock_db, note=note_paid)
    assert res_paid["fine_amount"] == Decimal("0.00")
    assert res_paid["interest_amount"] == Decimal("0.00")
    
    note_zero = PromissoryNote(
        original_amount=Decimal("100.00"),
        paid_amount=Decimal("100.00"),
        due_date=date.today() - timedelta(days=10),
        status=PromissoryNoteStatus.PENDING.value 
    )
    res_zero = calculate_interest_and_fine_for_note(mock_db, note=note_zero)
    assert res_zero["fine_amount"] == Decimal("0.00")