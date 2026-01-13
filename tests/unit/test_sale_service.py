import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock
from app.services.sale_service import (
    _last_day_of_month, 
    add_months, 
    _split_amount,
    create_sale_and_promissory_notes,
    get_sales,
    get_sale_by_id,
    delete_sale,
    update_sale
)
from app.schemas.sale_schema import SaleCreate, SaleUpdate
from app.models.customer import Customer
from app.models.sale import Sale
from app.models.promissory_note import PromissoryNote, PromissoryNoteStatus

# --- Testes de Funções Auxiliares ---
def test_last_day_february_leap_year():
    assert _last_day_of_month(2024, 2) == 29

def test_last_day_february_non_leap_year():
    assert _last_day_of_month(2023, 2) == 28

def test_last_day_30_days_months():
    assert _last_day_of_month(2023, 4) == 30
    assert _last_day_of_month(2023, 12) == 31 

def test_add_months_logic():
    d = date(2023, 1, 31)
    assert add_months(d, 1) == date(2023, 2, 28)

def test_split_amount_logic():
    parts = _split_amount(Decimal("100.00"), 3)
    assert sum(parts) == Decimal("100.00")
    assert len(parts) == 3

# --- Testes de Negócio ---

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
        down_payment=Decimal("150.00"), installments_count=1,
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

def test_get_sales_filters():
    mock_db = MagicMock()
    mock_query = mock_db.query.return_value
    mock_query.filter.return_value = mock_query
    mock_query.join.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = []

    get_sales(mock_db, user_id=1, client_name="João")
    
    assert mock_query.filter.call_count >= 1
    assert mock_query.join.call_count == 1 

def test_get_sale_by_id():
    mock_db = MagicMock()
    mock_sale = Sale(id=1)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_sale
    assert get_sale_by_id(mock_db, 1) == mock_sale

def test_delete_sale_success():
    mock_db = MagicMock()
    mock_sale = Sale(id=1)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_sale
    assert delete_sale(mock_db, 1) is True
    mock_db.delete.assert_called_with(mock_sale)
    mock_db.commit.assert_called_once()

def test_delete_sale_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    assert delete_sale(mock_db, 99) is False

def test_update_sale_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(ValueError, match="Venda não encontrada"):
        update_sale(mock_db, 99, SaleUpdate(description="X"))

def test_update_sale_financial_change_blocked_by_paid_notes():
    mock_db = MagicMock()
    sale = Sale(id=1, total_amount=Decimal("100.00"), installments_count=2, down_payment=0, first_installment_date=date.today())
    mock_db.query.return_value.filter.return_value.first.return_value = sale
    paid_note = PromissoryNote(status=PromissoryNoteStatus.PAID.value)
    mock_db.query.return_value.filter.return_value.all.return_value = [paid_note]
    
    with pytest.raises(ValueError, match="Não é possível alterar valores"):
        update_sale(mock_db, 1, SaleUpdate(total_amount=Decimal("200.00")))

def test_update_sale_financial_change_success():
    """Altera valor e recalcula parcelas (nenhuma paga)"""
    mock_db = MagicMock()
    sale = Sale(
        id=1, 
        total_amount=Decimal("100.00"), 
        down_payment=Decimal("0.00"),
        installments_count=2, 
        first_installment_date=date(2023, 1, 1)
    )
    
    sale_query_mock = MagicMock()
    note_query_mock = MagicMock()
    
    def side_effect_query(model):
        if model == Sale:
            return sale_query_mock
        elif model == PromissoryNote:
            return note_query_mock
        return MagicMock()

    mock_db.query.side_effect = side_effect_query
    
    # Configura retorno da Venda
    sale_query_mock.filter.return_value.first.return_value = sale
    
    # Configura retorno das Notas (2 chamadas: 1ª validação, 2ª retorno final)
    note_old = PromissoryNote(status="pending", paid_amount=Decimal(0))
    new_notes_list = [PromissoryNote(installment_number=i) for i in range(1, 4)]
    
    note_query_mock.filter.return_value.all.side_effect = [[note_old], new_notes_list]
    
    # Executa
    data = SaleUpdate(total_amount=Decimal("300.00"), installments_count=3)
    updated_sale, new_notes = update_sale(mock_db, 1, data)
    
    assert note_query_mock.filter.return_value.delete.called
    assert len(new_notes) == 3
    assert updated_sale.total_amount == Decimal("300.00")

def test_update_sale_simple_change():
    mock_db = MagicMock()
    sale = Sale(id=1, description="Antiga")
    mock_db.query.return_value.filter.return_value.first.return_value = sale
    mock_db.query.return_value.filter.return_value.all.return_value = [] 
    
    data = SaleUpdate(description="Nova Descrição")
    updated_sale, notes = update_sale(mock_db, 1, data)
    
    assert updated_sale.description == "Nova Descrição"
    assert not mock_db.query(PromissoryNote).filter().delete.called

def test_update_sale_customer_change():
    mock_db = MagicMock()
    sale = Sale(id=1, customer_id=10, description="Old")
    
    mock_db.query.return_value.filter.return_value.first.return_value = sale
    mock_db.query.return_value.filter.return_value.all.return_value = [] 
    
    data = SaleUpdate(customer_id=20)
    updated_sale, notes = update_sale(mock_db, 1, data)
    
    assert updated_sale.customer_id == 20
    assert not mock_db.query(PromissoryNote).filter().delete.called