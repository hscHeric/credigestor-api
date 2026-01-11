from decimal import Decimal
from datetime import date
from unittest.mock import MagicMock
from app.services.promissory_note_service import get_promissory_note_by_id, list_promissory_notes
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
    sale_mock = MagicMock(id=10, customer_id=5)
    cust_mock = MagicMock(id=5, full_name="Cliente Teste")

    mock_query = mock_db.query.return_value
    mock_query.join.return_value = mock_query  # O join retorna a própria query
    mock_query.filter.return_value = mock_query # O filter retorna a própria query
    mock_query.order_by.return_value = mock_query # O order_by retorna a própria query
    
    mock_query.all.return_value = [(note_mock, sale_mock, cust_mock)]

    result = list_promissory_notes(
        mock_db, 
        status="pending", 
        due_from=date(2023, 1, 1),
        due_to=date(2023, 12, 31)
    )

    assert result["total"] == 1
    assert result["items"][0]["customer_name"] == "Cliente Teste"
    assert result["items"][0]["outstanding_balance"] == Decimal("100.00")
    
    assert mock_query.filter.call_count >= 1

def test_list_promissory_notes_empty():
    mock_db = MagicMock()
    mock_query = mock_db.query.return_value
    
    mock_query.join.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.all.return_value = [] 

    result = list_promissory_notes(mock_db, customer_id=99)

    assert result["total"] == 0
    assert result["items"] == []
    assert "MSG13" in result["message"]