import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock
from app.services.sale_service import (
    _last_day_of_month, 
    add_months, 
    _split_amount,
    create_sale_and_promissory_notes
)
from app.schemas.sale_schema import SaleCreate
from app.models.customer import Customer

# Testes de Funções Auxiliares
def test_last_day_february_leap_year():
    assert _last_day_of_month(2024, 2) == 29

def test_last_day_february_non_leap_year():
    assert _last_day_of_month(2023, 2) == 28

def test_last_day_30_days_months():
    assert _last_day_of_month(2023, 4) == 30

def test_add_months_logic():
    d = date(2023, 1, 31)
    assert add_months(d, 1) == date(2023, 2, 28)

def test_split_amount_logic():
    parts = _split_amount(Decimal("100.00"), 3)
    assert sum(parts) == Decimal("100.00")
    assert len(parts) == 3

# Testes de Negócio

def test_create_sale_customer_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    data = MagicMock()
    data.customer_id = 999

    with pytest.raises(ValueError, match="Cliente não encontrado"):
        create_sale_and_promissory_notes(mock_db, user_id=1, data=data)

def test_create_sale_invalid_installments():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = Customer(id=1)
    
    data_mock = MagicMock()
    data_mock.customer_id = 1
    data_mock.installments_count = 0
    data_mock.down_payment = Decimal("0.00")
    data_mock.total_amount = Decimal("100.00")

    with pytest.raises(ValueError, match="MSG09"):
        create_sale_and_promissory_notes(mock_db, user_id=1, data=data_mock)

def test_create_sale_down_payment_too_high():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = Customer(id=1)
    
    data = SaleCreate(
        customer_id=1, user_id=1, total_amount=Decimal("100.00"),
        down_payment=Decimal("150.00"), 
        installments_count=1,
        first_installment_date=date.today(), description="Teste"
    )

    with pytest.raises(ValueError, match="Entrada não pode ser maior"):
        create_sale_and_promissory_notes(mock_db, user_id=1, data=data)

def test_create_sale_success_flow():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = Customer(id=1)
    
    data = SaleCreate(
        customer_id=1, user_id=1, total_amount=Decimal("100.00"),
        down_payment=Decimal("20.00"), installments_count=2,
        first_installment_date=date(2023, 1, 1), description="Venda OK"
    )

    sale, notes = create_sale_and_promissory_notes(mock_db, user_id=1, data=data)

    assert mock_db.add.call_count == 3 
    mock_db.commit.assert_called_once()
    assert sale.total_amount == Decimal("100.00")
    assert len(notes) == 2