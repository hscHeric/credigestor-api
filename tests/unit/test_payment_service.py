import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import MagicMock, patch

from app.services.payment_service import register_payment
from app.schemas.payment_schema import PaymentCreate
from app.models.promissory_note import PromissoryNote, PromissoryNoteStatus

@patch("app.services.payment_service.calculate_interest_and_fine_for_note")
def test_register_payment_full_success(mock_calc_interest):
    mock_calc_interest.return_value = {"interest_amount": Decimal("0.00"), "fine_amount": Decimal("0.00")}
    mock_db = MagicMock()
    
    note = PromissoryNote(
        id=1, original_amount=Decimal("100.00"), paid_amount=Decimal("0.00"),
        status=PromissoryNoteStatus.PENDING.value
    )
    mock_db.query.return_value.filter.return_value.first.return_value = note

    payload = PaymentCreate(amount_paid=Decimal("100.00"), payment_date=date.today())
    register_payment(mock_db, promissory_note_id=1, data=payload)

    assert note.status == PromissoryNoteStatus.PAID.value
    assert note.paid_amount == Decimal("100.00")

@patch("app.services.payment_service.calculate_interest_and_fine_for_note")
def test_register_payment_partial_success(mock_calc_interest):
    """Testa pagamento parcial de uma promissória"""
    mock_calc_interest.return_value = {"interest_amount": Decimal("0.00"), "fine_amount": Decimal("0.00")}
    mock_db = MagicMock()
    
    note = PromissoryNote(
        id=1, original_amount=Decimal("100.00"), paid_amount=Decimal("0.00"),
        status=PromissoryNoteStatus.PENDING.value
    )
    mock_db.query.return_value.filter.return_value.first.return_value = note

    payload = PaymentCreate(amount_paid=Decimal("40.00"), payment_date=date.today())
    register_payment(mock_db, promissory_note_id=1, data=payload)

    assert note.status == PromissoryNoteStatus.PARTIAL_PAYMENT.value
    assert note.paid_amount == Decimal("40.00")
    assert note.payment_date is None

def test_register_payment_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    payload = PaymentCreate(amount_paid=Decimal("10.00"), payment_date=date.today())
    
    with pytest.raises(ValueError, match="Promissória não encontrada"):
        register_payment(mock_db, promissory_note_id=99, data=payload)

def test_register_payment_zero_amount_defensive():
    mock_db = MagicMock()
    
    note = PromissoryNote(
        id=1, 
        status=PromissoryNoteStatus.PENDING.value,
        original_amount=Decimal("100.00"),
        paid_amount=Decimal("0.00")
    )
    mock_db.query.return_value.filter.return_value.first.return_value = note

    # Mock payload
    payload_mock = MagicMock()
    payload_mock.amount_paid = Decimal("0.00")

    with pytest.raises(ValueError, match="Valor pago deve ser maior que zero"):
        register_payment(mock_db, promissory_note_id=1, data=payload_mock)

def test_register_payment_greater_than_debt():
    mock_db = MagicMock()
    note = PromissoryNote(
        id=1, original_amount=Decimal("100.00"), paid_amount=Decimal("0.00"),
        status=PromissoryNoteStatus.PENDING.value
    )
    mock_db.query.return_value.filter.return_value.first.return_value = note

    payload = PaymentCreate(amount_paid=Decimal("101.00"), payment_date=date.today())
    with pytest.raises(ValueError, match="MSG18"):
        register_payment(mock_db, promissory_note_id=1, data=payload)

def test_register_payment_already_paid():
    mock_db = MagicMock()
    note = PromissoryNote(
        id=1, original_amount=Decimal("100.00"), paid_amount=Decimal("100.00"),
        status=PromissoryNoteStatus.PAID.value
    )
    mock_db.query.return_value.filter.return_value.first.return_value = note

    payload = PaymentCreate(amount_paid=Decimal("10.00"), payment_date=date.today())
    with pytest.raises(ValueError, match="MSG11"):
        register_payment(mock_db, promissory_note_id=1, data=payload)