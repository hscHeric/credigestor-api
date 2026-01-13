from decimal import Decimal
from datetime import date
from unittest.mock import MagicMock
from app.services.promissory_note_service import get_promissory_note_by_id, list_promissory_notes
from app.models.promissory_note import PromissoryNote
import pytest
from unittest.mock import MagicMock
from app.services.promissory_note_service import update_promissory_note_status
from app.models.promissory_note import PromissoryNote

def test_get_promissory_note_by_id():
    mock_db = MagicMock()
    note = PromissoryNote(id=1)
    mock_db.query.return_value.filter.return_value.first.return_value = note

    result = get_promissory_note_by_id(mock_db, 1)
    assert result.id == 1

def test_list_promissory_notes_with_data():
    """Testa listagem com dados para entrar no loop e cobrir a montagem do item"""
    mock_db = MagicMock()
    
    # Cria Mocks para os objetos retornados pelo banco (Nota, Venda, Cliente)
    note_mock = MagicMock(
        id=1, 
        sale_id=10, 
        installment_number=1, 
        due_date=date(2023, 5, 10), 
        original_amount=Decimal("100.00"), 
        paid_amount=Decimal("0.00"), 
        status="pending",
        created_at=date.today(),
        updated_at=date.today()
    )
    note_mock.original_amount = Decimal("100.00")
    note_mock.paid_amount = Decimal("0.00")
    
    sale_mock = MagicMock(id=10, customer_id=5)
    cust_mock = MagicMock(id=5, full_name="Cliente Teste")

    # 2. Configura o Mock do Banco para encadeamento
    mock_query = mock_db.query.return_value
    mock_query.join.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    
    mock_query.all.return_value = [(note_mock, sale_mock, cust_mock)]

    result = list_promissory_notes(
        mock_db, 
        status="pending", 
        due_from=date(2023, 1, 1),
        due_to=date(2023, 12, 31)
    )

    assert result["total"] == 1
    assert result["items"][0]["customer_name"] == "Cliente Teste"
    
def test_list_promissory_notes_empty():
    mock_db = MagicMock()
    mock_query = mock_db.query.return_value
    mock_query.join.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.all.return_value = [] # Lista vazia

    result = list_promissory_notes(mock_db, customer_id=99)

    assert result["total"] == 0
    assert "MSG13" in result["message"]
    
def test_update_promissory_note_status_success():
    mock_db = MagicMock()
    note = PromissoryNote(id=1, status="pending")
    mock_db.query.return_value.filter.return_value.first.return_value = note
    
    updated = update_promissory_note_status(mock_db, 1, "paid")
    
    assert updated.status == "paid"
    mock_db.commit.assert_called()
    mock_db.refresh.assert_called()

def test_update_promissory_note_status_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(ValueError, match="Promissória não encontrada"):
        update_promissory_note_status(mock_db, 99, "paid")
    
