import pytest
from unittest.mock import MagicMock
from decimal import Decimal
from datetime import date
from app.services.payment_receipt_service import build_payment_receipt_pdf, _money
from app.models.payment import Payment
from app.models.promissory_note import PromissoryNote
from app.models.sale import Sale
from app.models.customer import Customer
from app.models.system_config import SystemConfig

# --- Teste da Função Auxiliar ---

def test_money_helper_exception():
    class BadObject:
        def __format__(self, format_spec):
            raise ValueError("Erro de formato")
        def __str__(self):
            return "FallbackString"
    
    assert _money(BadObject()) == "FallbackString"

# --- Testes da Função Principal ---
def test_build_payment_receipt_success():
    mock_db = MagicMock()
    
    payment = Payment(
        id=1, 
        promissory_note_id=2, 
        amount_paid=Decimal("50.00"), 
        interest_amount=Decimal("0.00"), 
        fine_amount=Decimal("0.00"), 
        payment_date=date.today()
    )
    
    note = PromissoryNote(id=2, sale_id=3, installment_number=1, due_date=date.today())
    sale = Sale(id=3, customer_id=4)
    customer = Customer(id=4, full_name="João", cpf="123", phone="999", email="a@a.com", address="Rua A")
    config = SystemConfig(company_name="Empresa Teste")
    
    def side_effect_query(model):
        m = MagicMock()
        if model == Payment:
            m.filter.return_value.first.return_value = payment
        elif model == PromissoryNote:
            m.filter.return_value.first.return_value = note
        elif model == Sale:
            m.filter.return_value.first.return_value = sale
        elif model == Customer:
            m.filter.return_value.first.return_value = customer
        elif model == SystemConfig:
            m.order_by.return_value.first.return_value = config
        return m

    mock_db.query.side_effect = side_effect_query

    pdf_bytes = build_payment_receipt_pdf(mock_db, payment_id=1)
    
    assert pdf_bytes is not None
    assert pdf_bytes.startswith(b"%PDF")

def test_build_payment_receipt_payment_not_found():
    """Testa Pagamento não encontrado """
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    assert build_payment_receipt_pdf(mock_db, payment_id=99) is None

def test_build_payment_receipt_note_not_found():
    """Testa Nota Promissória não encontrada """
    mock_db = MagicMock()
    payment = MagicMock(promissory_note_id=1)
    
    def side_effect(model):
        m = MagicMock()
        if model == Payment:
            m.filter.return_value.first.return_value = payment
        elif model == PromissoryNote:
            m.filter.return_value.first.return_value = None 
        return m
        
    mock_db.query.side_effect = side_effect
    assert build_payment_receipt_pdf(mock_db, payment_id=1) is None

def test_build_payment_receipt_sale_not_found():
    """Testa Venda não encontrada """
    mock_db = MagicMock()
    payment = MagicMock(promissory_note_id=1)
    note = MagicMock(sale_id=2)
    
    def side_effect(model):
        m = MagicMock()
        if model == Payment:
            m.filter.return_value.first.return_value = payment
        elif model == PromissoryNote:
            m.filter.return_value.first.return_value = note
        elif model == Sale:
            m.filter.return_value.first.return_value = None 
        return m
        
    mock_db.query.side_effect = side_effect
    assert build_payment_receipt_pdf(mock_db, payment_id=1) is None

def test_build_payment_receipt_customer_not_found():
    """Testa Cliente não encontrado """
    mock_db = MagicMock()
    payment = MagicMock(promissory_note_id=1)
    note = MagicMock(sale_id=2)
    sale = MagicMock(customer_id=3)
    
    def side_effect(model):
        m = MagicMock()
        if model == Payment:
            m.filter.return_value.first.return_value = payment
        elif model == PromissoryNote:
            m.filter.return_value.first.return_value = note
        elif model == Sale:
            m.filter.return_value.first.return_value = sale
        elif model == Customer:
            m.filter.return_value.first.return_value = None 
        return m
        
    mock_db.query.side_effect = side_effect
    assert build_payment_receipt_pdf(mock_db, payment_id=1) is None