from unittest.mock import MagicMock
from datetime import date
from app.services.promissory_note_service import get_promissory_note_by_id, list_promissory_notes
from app.models.promissory_note import PromissoryNote

def test_get_promissory_note_by_id():
    mock_db = MagicMock()
    note = PromissoryNote(id=1)
    mock_db.query.return_value.filter.return_value.first.return_value = note

    result = get_promissory_note_by_id(mock_db, 1)
    assert result.id == 1

def test_list_promissory_notes_filters():
    mock_db = MagicMock()
    mock_query = mock_db.query.return_value
    
    # Simula cadeia de filtros
    mock_query.filter.return_value.filter.return_value.filter.return_value.order_by.return_value.all.return_value = []

    list_promissory_notes(
        mock_db, 
        status="pending", 
        due_date_from=date(2023, 1, 1), 
        due_date_to=date(2023, 1, 31)
    )
    assert mock_query.filter.call_count >= 1

def test_list_promissory_notes_by_customer():
    """Testa filtro por cliente que exige Join"""
    mock_db = MagicMock()
    mock_query = mock_db.query.return_value
    
    mock_join = mock_query.join.return_value
    mock_join.filter.return_value.order_by.return_value.all.return_value = []

    list_promissory_notes(mock_db, customer_id=10)
    
    # Verifica se o Join foi chamado
    mock_query.join.assert_called()