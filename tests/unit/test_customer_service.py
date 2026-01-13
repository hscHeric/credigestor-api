import pytest
from unittest.mock import MagicMock
from pydantic import ValidationError  
from app.services.customer_service import (
    create_customer, 
    update_customer, 
    list_customers, 
    get_customer_by_id, 
    get_customer_by_cpf
)
from app.schemas.customer_schema import CustomerCreate, CustomerUpdate, CustomerOut
from app.models.customer import Customer

def test_create_customer_success():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    data = CustomerCreate(
        full_name="Teste", 
        cpf="111.111.111-11", 
        phone="123",
        active=True
    )
    customer = create_customer(mock_db, data)
    assert customer.cpf == "11111111111"

def test_create_customer_duplicate_cpf():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()
    data = CustomerCreate(
        full_name="Teste 2", 
        cpf="111.111.111-11", 
        phone="123"
    )
    with pytest.raises(ValueError, match="MSG05"):
        create_customer(mock_db, data)


def test_customer_schema_invalid_cpf():
    """Tenta criar esquema com CPF inválido para disparar o validador"""
    with pytest.raises(ValidationError, match="CPF deve conter 11 dígitos"):
        CustomerCreate(
            full_name="Teste CPF Ruim", 
            cpf="12345", 
            phone="123"
        )

def test_get_customer_by_cpf():
    mock_db = MagicMock()
    fake_customer = Customer(id=1, cpf="111.111.111-11")
    mock_db.query.return_value.filter.return_value.first.return_value = fake_customer
    result = get_customer_by_cpf(mock_db, "111.111.111-11")
    assert result is not None

def test_get_customer_by_id():
    mock_db = MagicMock()
    fake_customer = Customer(id=99, full_name="Busca por ID")
    mock_db.query.return_value.filter.return_value.first.return_value = fake_customer
    result = get_customer_by_id(mock_db, 99)
    assert result.id == 99

def test_list_customers():
    mock_db = MagicMock()
    mock_db.query.return_value.order_by.return_value.all.return_value = [Customer(id=1)]
    result = list_customers(mock_db)
    assert len(result) == 1

def test_update_customer():
    mock_db = MagicMock()
    customer = Customer(id=1, full_name="Antigo", phone="000")
    update_data = CustomerUpdate(full_name="Novo", phone="999")
    updated = update_customer(mock_db, customer, update_data)
    assert updated.full_name == "Novo"

def test_customer_out_cpf_formatting():
    """Testa se o validador de saída formata o CPF corretamente"""
    data = {
        "id": 1, 
        "full_name": "Teste", 
        "cpf": "11122233344", 
        "phone": "123",  
        "email": "a@a.com"
    }
    
    customer_out = CustomerOut(**data)
    assert customer_out.cpf == "111.222.333-44"

def test_customer_out_cpf_already_formatted():
    """Testa se o validador ignora se já vier formatado ou inválido"""
    data = {
        "id": 1, 
        "full_name": "Teste", 
        "cpf": "111.222.333-44", 
        "phone": "123"
    }
    customer_out = CustomerOut(**data)
    assert customer_out.cpf == "111.222.333-44"