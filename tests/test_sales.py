import pytest
from fastapi.testclient import TestClient
from datetime import date
from app.main import app
from app.models.user import User
from app.router.auth_routes import get_current_user

# Teste de integração 2 - rotas de vendas

@pytest.fixture(autouse=True)
def mock_login():
    def mock_get_current_user():
        return User(id=1, email="admin@teste.com", role="admin", active=True)
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield

def test_create_sale_success(client: TestClient):
    # 1. Cria cliente
    client.post("/api/customers", json={"full_name":"Comprador", "cpf":"111.111.111-11", "phone":"11"})
    cust_id = 1 

    sale_data = {
        "customer_id": cust_id,
        "total_amount": 1000.00,
        "down_payment": 100.00, # Sobra 900
        "installments_count": 3, # 3x de 300
        "first_installment_date": str(date.today()),
        "description": "Venda Teste"
    }
    response = client.post("/api/sales", json=sale_data)

    assert response.status_code == 201
    data = response.json()
    assert float(data["total_amount"]) == 1000.00
    assert len(data["promissory_notes"]) == 3
    assert float(data["promissory_notes"][0]["original_amount"]) == 300.00

def test_create_sale_customer_not_found(client: TestClient):
    """Teste: Vender para cliente inexistente tem q dar 404"""
    sale_data = {
        "customer_id": 9999, # Não existe
        "total_amount": 1000.00,
        "down_payment": 0,
        "installments_count": 1,
        "first_installment_date": str(date.today())
    }
    response = client.post("/api/sales", json=sale_data)
    
    assert response.status_code == 404
    assert "Cliente não encontrado" in response.json()["detail"]

def test_create_sale_invalid_down_payment(client: TestClient):
    """Teste: Entrada maior que total deve dar 400"""
    client.post("/api/customers", json={"full_name":"F", "cpf":"000.000.000-00", "phone":"1"})
    
    sale_data = {
        "customer_id": 1,
        "total_amount": 500.00,
        "down_payment": 600.00, 
        "installments_count": 1,
        "first_installment_date": str(date.today())
    }
    response = client.post("/api/sales", json=sale_data)
    
    assert response.status_code == 400