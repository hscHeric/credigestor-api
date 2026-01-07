import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.router.auth_routes import get_current_user

# teste de integração 1 - rotas de clientes
# Dados de teste
client_data = {
    "full_name": "Teste da Silva",
    "cpf": "111.222.333-44",
    "phone": "11999999999",
    "email": "teste@cliente.com",
    "address": "Rua Fake, 123",
    "active": True
}

@pytest.fixture(autouse=True)
def mock_login():
    """
    função roda automaticamente antes de CADA teste.
    garante que o override de login seja reaplicado sempre,
    mesmo que o conftest.py limpe tudo.
    """
    def mock_get_current_user():
        return User(id=1, email="admin@teste.com", role="admin", active=True)

    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    yield 
    
def test_create_customer_success(client: TestClient):
    response = client.post("/api/customers", json=client_data)
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == client_data["full_name"]
    assert "id" in data

def test_create_customer_invalid_cpf(client: TestClient):
    bad_data = client_data.copy()
    bad_data["cpf"] = "12345678900" # Formato inválido
    response = client.post("/api/customers", json=bad_data)
    assert response.status_code == 422

def test_list_customers(client: TestClient):
    # Cria um para garantir
    client.post("/api/customers", json=client_data)
    
    response = client.get("/api/customers")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_customer_by_id(client: TestClient):
    # Cria
    create_res = client.post("/api/customers", json=client_data)
    assert create_res.status_code == 201 # Garante que criou antes de tentar ler
    customer_id = create_res.json()["id"]
    
    # Busca
    response = client.get(f"/api/customers/{customer_id}")
    assert response.status_code == 200
    assert response.json()["id"] == customer_id

def test_get_customer_not_found(client: TestClient):
    response = client.get("/api/customers/9999")
    assert response.status_code == 404
    
def test_create_customer_duplicate_cpf(client: TestClient):
    """Teste: Deve bloquear cadastro de CPF já existente (Regra de Negócio)"""
    # 1. Cria o primeiro (Original)
    client.post("/api/customers", json=client_data)
    
    # 2. Tenta criar o segundo (Clone)
    clone_data = client_data.copy()
    clone_data["full_name"] = "Clone da Silva"
    
    response = client.post("/api/customers", json=clone_data)
    
    assert response.status_code == 400
    assert "MSG05" in response.json()["detail"]

def test_update_customer(client: TestClient):
    """Teste: Deve atualizar os dados de um cliente existente"""
    # 1. Cria
    res_create = client.post("/api/customers", json=client_data)
    customer_id = res_create.json()["id"]
    
    # 2. Atualiza 
    update_data = {
        "full_name": "Teste Atualizado da Silva",
        "phone": "11900000000"
    }
    
    response = client.put(f"/api/customers/{customer_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Teste Atualizado da Silva"
    assert data["phone"] == "11900000000"
    assert data["cpf"] == client_data["cpf"] # CPF não deve mudar
    
def test_update_customer_not_found(client: TestClient):
    """Teste: Tentar atualizar um cliente que não existe deve dar 404"""
    payload = {
        "full_name": "Nome Fantasma",
        "phone": "11900000000"
    }
    # Tenta atualizar o ID 9999 (que não existe)
    response = client.put("/api/customers/9999", json=payload)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Cliente não encontrado"