from unittest.mock import MagicMock
from decimal import Decimal
from datetime import date, timedelta
from app.services.report_service import delinquency_report

def test_delinquency_report():
    mock_db = MagicMock()
    
    today = date.today()
    overdue_date = today - timedelta(days=10)
    
    note = MagicMock(
        id=1, original_amount=Decimal("100.00"), paid_amount=Decimal("0.00"),
        due_date=overdue_date, status="pending"
    )
    sale = MagicMock(id=10, customer_id=5)
    customer = MagicMock(id=5, full_name="João", phone="123")
    
    mock_db.query.return_value.join.return_value.join.return_value.filter.return_value.filter.return_value.order_by.return_value.all.return_value = [
        (note, sale, customer)
    ]

    report = delinquency_report(mock_db)

    assert report["total_customers"] == 1
    assert report["total_due_all"] == Decimal("100.00")
    
    cust_data = report["customers"][0]
    assert cust_data["customer_name"] == "João"
    assert cust_data["overdue_installments_count"] == 1
    assert cust_data["installments"][0]["days_overdue"] == 10

def test_delinquency_report_filters():
    """Testa os filtros de data (due_from e due_to)"""
    mock_db = MagicMock()
    
    mock_query = mock_db.query.return_value.join.return_value.join.return_value
    mock_query.filter.return_value = mock_query
    
    mock_query.order_by.return_value.all.return_value = []
    
    d1 = date(2023, 1, 1)
    d2 = date(2023, 1, 31)
    
    delinquency_report(mock_db, due_from=d1, due_to=d2)
    
    assert mock_query.filter.call_count >= 4