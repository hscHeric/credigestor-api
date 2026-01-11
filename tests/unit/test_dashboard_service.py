from unittest.mock import MagicMock
from decimal import Decimal
from datetime import date
from app.services.dashboard_service import get_dashboard

def test_get_dashboard_values():
    mock_db = MagicMock()

    mock_db.query.return_value.filter.return_value.scalar.side_effect = [
        Decimal("5000.00"), 
        Decimal("1000.00"), 
        Decimal("2500.00")  
    ]
    
    q1 = MagicMock()
    q1.filter.return_value.scalar.return_value = Decimal("5000.00") 
    
    q2 = MagicMock()
    q2.filter.return_value.filter.return_value.scalar.return_value = Decimal("1000.00") 
    
    q3 = MagicMock()
    q3.filter.return_value.filter.return_value.scalar.return_value = Decimal("2500.00")
    
    q4 = MagicMock() 

    note_mock = MagicMock(
        id=1, sale_id=10, original_amount=Decimal("100.00"), 
        paid_amount=Decimal("0.00"), due_date=date.today(), status="pending"
    )
    q4.join.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
        (note_mock, 99)
    ]

    mock_db.query.side_effect = [q1, q2, q3, q4]

    result = get_dashboard(mock_db)

    assert result["total_to_receive"] == Decimal("5000.00")
    assert result["total_overdue"] == Decimal("1000.00")
    assert result["received_last_30_days"] == Decimal("2500.00")
    assert len(result["next_due"]) == 1
    assert result["next_due"][0]["customer_id"] == 99